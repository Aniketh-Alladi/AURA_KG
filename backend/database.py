from neo4j import GraphDatabase
import os

# Database details
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_AUTH = (
    os.getenv("NEO4J_USER", "neo4j"), 
    os.getenv("NEO4J_PASSWORD", "your_password")
)

# Global driver instance
driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

def get_session():
    """Returns a new Neo4j session instance."""
    return driver.session()