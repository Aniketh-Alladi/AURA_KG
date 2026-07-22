"""
AURA-KG Graph Builder Module.
Writes extracted nodes and relationships into Neo4j using idempotent Cypher MERGE queries adhering to graph constraints.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from backend.database import Neo4jDatabase

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Handles writing extracted entities and relationships into Neo4j graph database."""

    def __init__(self, db: Optional[Neo4jDatabase] = None) -> None:
        """
        Initialize GraphBuilder with Neo4j database instance.

        :param db: Neo4jDatabase instance. If None, instantiates a default connection.
        """
        self.db = db or Neo4jDatabase()

    def create_node(self, node_data: Dict[str, Any]) -> None:
        """
        Idempotently create or update a node in Neo4j using MERGE on its unique primary key.

        :param node_data: Node dictionary containing label, pk_field, pk_val, and properties.
        """
        label = node_data["label"]
        pk_field = node_data["pk_field"]
        pk_val = node_data["pk_val"]
        props = node_data.get("properties", {})

        # Cypher MERGE query template
        cypher = f"""
        MERGE (n:`{label}` {{ `{pk_field}`: $pk_val }})
        ON CREATE SET n += $props
        ON MATCH SET n += $props
        RETURN n.`{pk_field}` AS id
        """

        params = {
            "pk_val": pk_val,
            "props": props
        }

        try:
            self.db.execute_write(cypher, params)
            logger.debug("Successfully merged node (%s:`%s`='%s')", label, pk_field, pk_val)
        except Exception as e:
            logger.error("Failed to merge node (%s:`%s`='%s'): %s", label, pk_field, pk_val, str(e))
            raise

    def create_relationship(self, rel_data: Dict[str, Any]) -> None:
        """
        Idempotently create a relationship between two nodes in Neo4j using MERGE.

        :param rel_data: Relationship dictionary containing source/target labels, primary key fields/vals, and rel_type.
        """
        source_label = rel_data["source_label"]
        source_pk_field = rel_data["source_pk_field"]
        source_pk_val = rel_data["source_pk_val"]

        target_label = rel_data["target_label"]
        target_pk_field = rel_data["target_pk_field"]
        target_pk_val = rel_data["target_pk_val"]

        rel_type = rel_data["rel_type"]

        cypher = f"""
        MATCH (a:`{source_label}` {{ `{source_pk_field}`: $source_pk_val }})
        MATCH (b:`{target_label}` {{ `{target_pk_field}`: $target_pk_val }})
        MERGE (a)-[r:`{rel_type}`]->(b)
        RETURN type(r) AS rel
        """

        params = {
            "source_pk_val": source_pk_val,
            "target_pk_val": target_pk_val
        }

        try:
            self.db.execute_write(cypher, params)
            logger.debug(
                "Merged relationship (: %s {%s: '%s'}) -[:%s]-> (: %s {%s: '%s'})",
                source_label, source_pk_field, source_pk_val,
                rel_type,
                target_label, target_pk_field, target_pk_val
            )
        except Exception as e:
            logger.error("Failed to merge relationship: %s", str(e))
            raise

    def write_to_graph(
        self, nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Write a batch of nodes and relationships into Neo4j database.

        :param nodes: List of node dictionaries.
        :param relationships: List of relationship dictionaries.
        :return: Tuple of (nodes_processed_count, relationships_processed_count).
        """
        logger.info("Writing %d nodes and %d relationships to Neo4j...", len(nodes), len(relationships))
        
        # Deduplicate nodes by primary key value before writing
        seen_nodes = set()
        nodes_written = 0
        for node in nodes:
            pk_key = (node["label"], node["pk_val"])
            if pk_key not in seen_nodes:
                self.create_node(node)
                seen_nodes.add(pk_key)
                nodes_written += 1

        # Write relationships
        rels_written = 0
        for rel in relationships:
            self.create_relationship(rel)
            rels_written += 1

        logger.info("Graph write completed: %d node(s) merged, %d relationship(s) merged.", nodes_written, rels_written)
        return nodes_written, rels_written
