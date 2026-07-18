# run_constraints.py
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def run_constraints_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    # Split on semicolons, strip comments/blank statements
    statements = [
        s.strip() for s in content.split(";")
        if s.strip() and not s.strip().startswith("//")
    ]

    with driver.session() as session:
        for stmt in statements:
            # Remove comment lines within a statement block
            clean_stmt = "\n".join(
                line for line in stmt.split("\n") if not line.strip().startswith("//")
            ).strip()
            if clean_stmt:
                session.run(clean_stmt)
                print(f"Executed: {clean_stmt.splitlines()[0]}...")

if __name__ == "__main__":
    run_constraints_file("../graph/constraints.cypher")
    print("All constraints applied.")
    driver.close()