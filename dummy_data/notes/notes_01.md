Title: AURA-KG Sprint Notes — Week 3

Met with Varun and Tejus today to discuss the ingestion pipeline.
Varun is handling the Gmail API connector for AURA-KG's data pipeline.
We're targeting Neo4j as the graph database, using Cypher for queries.

Decided the Phase 2 deadline is August 15th — need the extraction
pipeline working by then. Aniketh is exploring FAISS for the vector
search layer, part of the retrieval feature.

Risk flagged: entity extraction accuracy with spaCy's small model
might not be good enough — may need to upgrade to a transformer model.