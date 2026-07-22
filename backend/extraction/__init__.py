"""
AURA-KG Extraction Pipeline Package.
Contains components for loading documents, entity extraction (NER), node classification,
relationship extraction, and Neo4j graph building.
"""

from backend.extraction.loader import DocumentLoader, load_documents
from backend.extraction.ner import SpacyNERExtractor
from backend.extraction.classifier import EntityClassifier
from backend.extraction.relationship_extractor import RelationshipExtractor
from backend.extraction.graph_builder import GraphBuilder
from backend.extraction.pipeline import ExtractionPipeline

__all__ = [
    "DocumentLoader",
    "load_documents",
    "SpacyNERExtractor",
    "EntityClassifier",
    "RelationshipExtractor",
    "GraphBuilder",
    "ExtractionPipeline",
]
