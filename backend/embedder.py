import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from backend.database import get_session  # Adjust import path if needed

# TODO: Import your Neo4j driver or session factory from backend.database
# TODO: Import OpenAI (or your chosen embedding provider)
# TODO: Import settings/config variables from backend.config
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def get_embedding(text: str) -> List[float]:
    """
    Takes a string of text and calls the embedding API.
    Returns a list of 1536 floats.
    """
    # TODO: Clean/strip input text
    # TODO: Call embedding API (e.g., text-embedding-3-small)
    # TODO: Return vector float array from response
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Cannot generate embedding for an empty string.")
    response = client.embeddings.create(    
        model="text-embedding-3-small",
        input=cleaned_text
    )
    return response.data[0].embedding
    


def fetch_unembedded_nodes(session) -> List[Dict[str, Any]]:
    """
    Queries Neo4j for nodes labeled :Entity that do not have an embedding set.
    """
    cypher = """
    MATCH (n:Entity)
    WHERE n.embedding IS NULL
    RETURN 
        n.id AS id, 
        coalesce(n.name, n.title, '') AS identifier, 
        coalesce(n.description, n.summary, '') AS details,
    labels(n) AS node_type
    """
    """
    // TODO: Write Cypher query to MATCH nodes labeled :Entity
    // TODO: Filter WHERE n.embedding IS NULL
    // TODO: RETURN node properties (id, name, description, title, etc.)
    """
    # TODO: Run query in session and return a list of dictionary objects
    result = session.run(cypher)

    return [record.data() for record in result]


def save_node_embedding(session, node_id: str, embedding: List[float]) -> None:
    """
    Updates a single node in Neo4j with its generated embedding vector.
    """
    cypher = """
    MATCH (n:Entity {id: $node_id})
    SET n.embedding = $embedding
    """
    """
    // TODO: Write Cypher query to MATCH node by ID
    // TODO: SET n.embedding = $embedding
    """
    # TODO: Run the write query using session.run()
    session.execute_write(lambda tx: tx.run(cypher, node_id=node_id, embedding=embedding))


def index_all_unembedded_nodes() -> None:
    """
    Orchestrates fetching, embedding, and writing embeddings back to Neo4j.
    """
    # Acquire database session
    with get_session() as session:
        # 1. Fetch nodes missing an embedding
        nodes = fetch_unembedded_nodes(session)
        
        total_nodes = len(nodes)
        if total_nodes == 0:
            print("No unembedded nodes found.")
            return

        print(f"Found {total_nodes} nodes to embed and index...\n")

        # 2. Loop over each node
        for index, node in enumerate(nodes, start=1):
            node_id = node["id"]
            identifier = node.get("identifier", "")
            details = node.get("details", "")

            # Combine name/title and description into a clean text string for embedding
            text_to_embed = f"{identifier}: {details}".strip(" :")

            if not text_to_embed:
                print(f"[{index}/{total_nodes}] Skipping node {node_id}: No text content available to embed.")
                continue

            # Generate embedding vector
            embedding = get_embedding(text_to_embed)

            # Write embedding back to Neo4j
            save_node_embedding(session, node_id=node_id, embedding=embedding)

            # Progress log
            print(f"[{index}/{total_nodes}] Indexed node '{identifier}' (ID: {node_id})")

        print("\nSuccessfully finished indexing all unembedded nodes!")
    


if __name__ == "__main__":
    # Test execution when run directly
    index_all_unembedded_nodes()