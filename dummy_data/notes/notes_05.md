# File: notes_evaluation_metrics.md
Title: Evaluation Metrics & RAG Triad
Date: July 24, 2026

Aniketh shared his research on evaluating the LLM & retrieval system. Since his role centers on Retrieval Quality, he's setting up a standalone evaluation dataset.

Details:
- He is using Ragas alongside FAISS to test faithfulness and answer relevance.
- This evaluation framework is a critical deliverable for Phase 1. 
- Met with Varun to ensure the evaluation text chunks map cleanly back to the original source documents parsed by the Python ingestion script. If the source metadata is lost in the graph database, debugging bad retrievals will be impossible.