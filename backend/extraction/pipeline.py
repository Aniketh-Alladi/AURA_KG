"""
AURA-KG NLP Extraction Pipeline Orchestrator.
Coordinates the end-to-end process: loading normalized documents, extracting entities (NER),
classifying nodes into domain schema types, extracting relationships, and storing the graph into Neo4j.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.config import Config
from backend.extraction.loader import load_documents
from backend.extraction.ner import SpacyNERExtractor
from backend.extraction.classifier import EntityClassifier
from backend.extraction.relationship_extractor import RelationshipExtractor
from backend.extraction.graph_builder import GraphBuilder

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set up logging configuration
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("extraction_pipeline")


class ExtractionPipeline:
    """Orchestrator for the AURA-KG NLP extraction pipeline."""

    def __init__(self, spacy_model: str = Config.SPACY_MODEL) -> None:
        """
        Initialize pipeline components.

        :param spacy_model: spaCy model name string.
        """
        logger.info("Initializing AURA-KG NLP Extraction Pipeline components...")
        self.ner_extractor = SpacyNERExtractor(model_name=spacy_model)
        self.classifier = EntityClassifier()
        self.rel_extractor = RelationshipExtractor()

    def process_text(self, text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Process a single raw text string to extract classified nodes and relationships.

        :param text: Raw text content string.
        :return: Tuple of (nodes list, relationships list).
        """
        extracted_nodes: List[Dict[str, Any]] = []
        extracted_rels: List[Dict[str, Any]] = []

        # 1. Extract NER entities
        raw_entities = self.ner_extractor.extract_entities(text)

        # Group entities by sentence for relationship extraction
        sentence_nodes_map: Dict[str, List[Dict[str, Any]]] = {}

        for ent in raw_entities:
            classified = self.classifier.classify(ent["text"], ent.get("spacy_label"))
            if classified:
                extracted_nodes.append(classified)

                sent_text = ent.get("sentence", text)
                if sent_text not in sentence_nodes_map:
                    sentence_nodes_map[sent_text] = []
                
                if classified not in sentence_nodes_map[sent_text]:
                    sentence_nodes_map[sent_text].append(classified)

        # 2. Extract Relationships sentence by sentence
        for sent_text, nodes in sentence_nodes_map.items():
            rels = self.rel_extractor.extract_relationships(sent_text, nodes)
            extracted_rels.extend(rels)

        return extracted_nodes, extracted_rels

    def run(self, input_path: str, write_to_db: bool = True) -> Tuple[int, int]:
        """
        Run extraction pipeline on the input document file or directory.

        :param input_path: Path to input JSON payload or directory of JSON documents.
        :param write_to_db: Whether to write extracted graph entities to Neo4j.
        :return: Tuple of total (nodes_count, relationships_count).
        """
        logger.info("🚀 Starting AURA-KG NLP Extraction Pipeline...")
        logger.info("Input path: %s", input_path)

        # Step 1: Load documents
        logger.info("Step 1/4: Loading normalized documents...")
        documents = load_documents(input_path)

        if not documents:
            logger.warning("No documents loaded. Pipeline finished.")
            return 0, 0

        all_nodes: List[Dict[str, Any]] = []
        all_relationships: List[Dict[str, Any]] = []

        # Step 2 & 3: Perform NER & Relationship Extraction across documents
        logger.info("Step 2 & 3: Performing NER, Node Classification & Relationship Extraction...")
        for idx, doc in enumerate(documents, start=1):
            source = doc.get("source_path") or f"doc_{idx}"
            raw_text = doc.get("raw_text", "")

            logger.info("Processing document [%d/%d]: %s", idx, len(documents), source)
            nodes, rels = self.process_text(raw_text)

            all_nodes.extend(nodes)
            all_relationships.extend(rels)

        logger.info(
            "Extracted a total of %d node mention(s) and %d relationship candidate(s).",
            len(all_nodes), len(all_relationships)
        )

        # Step 4: Write to Neo4j
        nodes_merged, rels_merged = 0, 0
        if write_to_db:
            logger.info("Step 4/4: Writing nodes and relationships into Neo4j graph database...")
            builder = GraphBuilder()
            nodes_merged, rels_merged = builder.write_to_graph(all_nodes, all_relationships)
            builder.db.close()
        else:
            logger.info("Step 4/4: DB writing skipped (write_to_db=False).")

        logger.info("✨ AURA-KG Extraction Pipeline Execution Complete!")
        logger.info("Summary: %d Nodes Merged, %d Relationships Merged.", nodes_merged, rels_merged)

        return nodes_merged, rels_merged


def main() -> None:
    """Main CLI entry point for running the pipeline."""
    parser = argparse.ArgumentParser(description="AURA-KG NLP Extraction Pipeline")
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=str(Config.DEFAULT_INPUT_FILE),
        help="Path to normalized_ingestion_output.json or directory containing document JSONs."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run extraction without writing to Neo4j database."
    )
    args = parser.parse_args()

    pipeline = ExtractionPipeline()
    pipeline.run(input_path=args.input, write_to_db=not args.dry_run)


if __name__ == "__main__":
    main()
