import os
from typing import List, Dict, Any

from backend.embedder import get_embedding
from backend.database import get_session


def vector_and_subgraph_search(
    session, 
    query_vector: List[float], 
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Executes a hybrid Cypher query that performs a vector similarity search 
    and immediately traverses 1-hop relationships outward.
    """
    cypher = """
    CALL db.index.vector.queryNodes('node_embedding_idx', $top_k, $query_vector)
    YIELD node, score

    OPTIONAL MATCH (node)-[r]-(neighbor)
    WHERE neighbor IS NOT NULL

    RETURN 
        node.id AS anchor_id,
        coalesce(node.name, node.title, '') AS anchor_name,
        coalesce(node.description, node.summary, '') AS anchor_desc,
        [label IN labels(node) WHERE label <> 'Entity'][0] AS anchor_type,
        score,
        collect({
            relationship: type(r),
            is_outgoing: startNode(r) = node,
            target_id: neighbor.id,
            target_name: coalesce(neighbor.name, neighbor.title, ''),
            target_desc: coalesce(neighbor.description, neighbor.summary, ''),
            target_type: [label IN labels(neighbor) WHERE label <> 'Entity'][0]
        }) AS connections
        """
    # Execute query passing parameters safely
    result = session.run(cypher, top_k=top_k, query_vector=query_vector)
    
    # Transform Neo4j Record objects into plain dictionaries
    return [record.data() for record in result]


def format_subgraph_context(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parses the raw graph query results into:
    1. A formatted text string ready to be injected into an LLM prompt.
    2. A deduplicated list of supporting nodes formatted for Nikshith's frontend highlight response.
    """
    context_lines = []
    supporting_nodes_map = {}

    for record in results:
        anchor_id = record.get("anchor_id")
        anchor_name = record.get("anchor_name")
        anchor_desc = record.get("anchor_desc")
        anchor_type = record.get("anchor_type")

        # Track anchor node for frontend highlighting
        if anchor_id and anchor_id not in supporting_nodes_map:
            supporting_nodes_map[anchor_id] = {
                "id": anchor_id,
                "name": anchor_name,
                "type": anchor_type or "Entity",
                "relevance": "primary_match"
            }

        # Build text string block for LLM prompt
        line = f"Entity: {anchor_name} ({anchor_type})\nDescription: {anchor_desc}\nConnections:"
        
        connections = record.get("connections", [])
        has_connections = False

        for conn in connections:
            target_id = conn.get("target_id")
            rel = conn.get("relationship")
            target_name = conn.get("target_name")
            target_desc = conn.get("target_desc")
            target_type = conn.get("target_type")

            if target_id:
                has_connections = True
                # Track neighbor node for frontend highlighting
                if target_id not in supporting_nodes_map:
                    supporting_nodes_map[target_id] = {
                        "id": target_id,
                        "name": target_name,
                        "type": target_type or "Entity",
                        "relevance": "connected_context"
                    }
                line += f"\n  - [{rel}] -> {target_name} ({target_type}): {target_desc}"

        if not has_connections:
            line += "\n  - None"

        context_lines.append(line)

    formatted_text = "\n\n".join(context_lines)
    supporting_nodes = list(supporting_nodes_map.values())

    return {
        "text_context": formatted_text,
        "supporting_nodes": supporting_nodes
    }


def retrieve_context(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Orchestrates the full retrieval flow:
    1. Embeds user query
    2. Runs hybrid Cypher query against Neo4j
    3. Formats results for downstream consumption (LLM prompt + API response)
    """
    # 1. Embed user query string
    query_vector = get_embedding(query)
    
    # 2. Acquire session and query graph database
    with get_session() as session:
        raw_results = vector_and_subgraph_search(
            session=session, 
            query_vector=query_vector, 
            top_k=top_k
        )
        
    # 3. Format context string and supporting metadata
    return format_subgraph_context(raw_results)


if __name__ == "__main__":
    # Test execution block when run directly
    test_query = "What tools does AURA-KG use?"
    
    print(f"Running retrieval for query: '{test_query}'...\n")
    retrieved_data = retrieve_context(test_query)
    
    print("=== FORMATTED LLM CONTEXT ===")
    print(retrieved_data["text_context"])
    
    print("\n=== SUPPORTING FRONTEND NODES ===")
    for node in retrieved_data["supporting_nodes"]:
        print(node)