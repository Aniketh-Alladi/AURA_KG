# File: notes_architecture_sync.md
Title: Architecture Sync & Component Mapping
Date: July 20, 2026

Sat down with Tejus to diagram the core NLP & graph construction phase. We confirmed that Tejus is stepping into the Lead Ontologist role for the project to ensure the schema holds up. 

Key architectural decisions:
- We are officially committing to Neo4j as the graph database. Cypher will be our primary query language.
- For the retrieval feature, Aniketh is owning the LLM & retrieval layer. He is currently benchmarking FAISS against LanceDB to handle the vector search layer.
- The immediate deliverable is a functional prototype with an example query session, which needs to be ready before we scale out.

Risk: Tejus noted that spaCy's small model might struggle with custom technical entities. We might need to swap it out for a fine-tuned Transformer model if edge extraction accuracy drops below 80%.