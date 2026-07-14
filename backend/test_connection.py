# test_connection.py
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful' AS message")
        print(result.single()["message"])

def insert_dummy_data():
    with driver.session() as session:
        session.run("""
            MERGE (p:Person {person_id: 'p1', name: 'Aniketh'})
            MERGE (r:Role {role_id: 'r1', title: 'LLM & Retrieval'})
            MERGE (proj:Project {project_id: 'proj1', name: 'AURA-KG'})
            MERGE (p)-[:ASSIGNED_TO]->(r)
            MERGE (r)-[:ASSIGNED_TO]->(proj)
        """)
        print("Dummy nodes and relationships inserted.")

def verify_data():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person)-[:ASSIGNED_TO]->(r:Role)-[:ASSIGNED_TO]->(proj:Project)
            RETURN p.name AS person, r.title AS role, proj.name AS project
        """)
        for record in result:
            print(record)

if __name__ == "__main__":
    test_connection()
    insert_dummy_data()
    verify_data()
    driver.close()