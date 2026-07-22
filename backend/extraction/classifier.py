"""
AURA-KG Node Classifier Module.
Classifies extracted entity mentions into AURA-KG domain node types using rule-based dictionary lookups,
keyword pattern matching, and fallback heuristics.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Primary Key Property Mapping for Neo4j Schema Constraints
PRIMARY_KEY_MAP = {
    "Person": "person_id",
    "Role": "role_id",
    "Project": "project_id",
    "Domain": "domain_id",
    "Tool": "tool_id",
    "Feature": "feature_id",
    "Phase": "phase_id",
    "Milestone": "milestone_id",
    "Outcome": "outcome_id",
    "Deliverable": "deliverable_id",
    "Dataset": "dataset_id",
}

# Domain Dictionary for Known Entities in AURA-KG
EXACT_TAXONOMY_MAP: Dict[str, str] = {
    # Team Members / People
    "tejus": "Person",
    "varun": "Person",
    "aniketh": "Person",
    "nikshith": "Person",
    
    # Projects
    "aura-kg": "Project",
    "aura kg": "Project",
    "aura": "Project",

    # Tools / Tech Stack
    "neo4j": "Tool",
    "docker": "Tool",
    "spacy": "Tool",
    "python": "Tool",
    "cypher": "Tool",
    "transformers": "Tool",
    "huggingface": "Tool",
    "fastapi": "Tool",
    "react": "Tool",
    "next.js": "Tool",

    # Roles
    "knowledge graph developer": "Role",
    "data ingestion developer": "Role",
    "llm developer": "Role",
    "retrieval developer": "Role",
    "frontend developer": "Role",
    "kg lead": "Role",

    # Domains
    "knowledge graphs + nlp": "Domain",
    "nlp": "Domain",
    "knowledge graphs": "Domain",
    "natural language processing": "Domain",

    # Features
    "knowledge graph storage": "Feature",
    "graph query engine": "Feature",
    "nlp extraction pipeline": "Feature",

    # Phases
    "graph design": "Phase",
    "data ingestion": "Phase",
    "nlp extraction": "Phase",
    "retrieval & llm": "Phase",
    "visualization": "Phase",

    # Milestones
    "milestone 1": "Milestone",
    "v1 release": "Milestone",

    # Datasets
    "dummy personal notes": "Dataset",
    "personal notes": "Dataset",

    # Outcomes
    "hands-on experience with knowledge graphs and neo4j": "Outcome",
}

# Keyword / Regex Rules
KEYWORD_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(tool|database|framework|library|docker|neo4j|spacy|python|git|api)\b", re.I), "Tool"),
    (re.compile(r"\b(project|assistant|system)\b", re.I), "Project"),
    (re.compile(r"\b(lead|developer|engineer|manager|role)\b", re.I), "Role"),
    (re.compile(r"\b(domain|field|nlp|ai|machine learning)\b", re.I), "Domain"),
    (re.compile(r"\b(feature|module|engine|pipeline|storage)\b", re.I), "Feature"),
    (re.compile(r"\b(phase|stage|sprint)\b", re.I), "Phase"),
    (re.compile(r"\b(milestone|deadline|target date)\b", re.I), "Milestone"),
    (re.compile(r"\b(deliverable|document|report|contract)\b", re.I), "Deliverable"),
    (re.compile(r"\b(dataset|corpus|notes|emails)\b", re.I), "Dataset"),
    (re.compile(r"\b(outcome|learning|result|experience)\b", re.I), "Outcome"),
]


class EntityClassifier:
    """Classifies NER entities into AURA-KG graph node types."""

    def __init__(self) -> None:
        """Initialize entity classifier dictionary maps and rule sets."""
        self.exact_map = EXACT_TAXONOMY_MAP
        self.keyword_rules = KEYWORD_RULES
        self._id_counters: Dict[str, int] = {k: 1 for k in PRIMARY_KEY_MAP.keys()}

    def normalize_name(self, name: str) -> str:
        """Clean and normalize entity text."""
        return name.strip()

    def generate_canonical_id(self, label: str, name: str) -> str:
        """
        Generate deterministic canonical ID for Neo4j primary key constraint.

        :param label: Target node label (e.g. Person, Tool, Project).
        :param name: Entity name string.
        :return: String ID (e.g., 'person_tejus', 'tool_neo4j', 'project_aura_kg').
        """
        clean_str = re.sub(r"[^\w]+", "_", name.strip().lower()).strip("_")
        prefix = label.lower()
        return f"{prefix}_{clean_str}"

    def classify(self, entity_text: str, spacy_label: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Classify entity text into node type and format property dict.

        :param entity_text: Raw entity mention text.
        :param spacy_label: Optional spaCy label (PERSON, ORG, PRODUCT, etc.).
        :return: Dict containing label, primary_key_field, primary_key_val, and properties, or None if unclassified.
        """
        if not entity_text or not entity_text.strip():
            return None

        clean_name = self.normalize_name(entity_text)
        lower_name = clean_name.lower()

        target_label: Optional[str] = None

        # 1. Exact Taxonomy Map Match
        if lower_name in self.exact_map:
            target_label = self.exact_map[lower_name]

        # 2. spaCy PERSON Label Mapping
        elif spacy_label == "PERSON":
            target_label = "Person"

        # 3. spaCy ORG / PRODUCT mapping heuristic
        elif spacy_label in ("ORG", "PRODUCT"):
            # Check keyword rules before defaulting
            for pattern, label in self.keyword_rules:
                if pattern.search(lower_name):
                    target_label = label
                    break
            if not target_label:
                target_label = "Tool" if spacy_label == "PRODUCT" else "Project"

        # 4. Keyword Rule Match
        else:
            for pattern, label in self.keyword_rules:
                if pattern.search(lower_name):
                    target_label = label
                    break

        if not target_label or target_label not in PRIMARY_KEY_MAP:
            logger.debug("Could not classify entity '%s' (spacy_label=%s)", entity_text, spacy_label)
            return None

        pk_field = PRIMARY_KEY_MAP[target_label]
        canonical_id = self.generate_canonical_id(target_label, clean_name)

        # Build initial property dict
        properties: Dict[str, Any] = {
            pk_field: canonical_id,
            "name": clean_name
        }

        # Add label-specific default attributes
        if target_label == "Role":
            properties["title"] = clean_name
            properties["responsibilities"] = f"Responsibilities for {clean_name}"
        elif target_label == "Project":
            properties["description"] = f"{clean_name} Project"
            properties["timeline"] = "Ongoing"
        elif target_label == "Tool":
            properties["category"] = "Software Tool"
        elif target_label == "Feature":
            properties["description"] = clean_name
            properties["status"] = "Planned"
        elif target_label == "Phase":
            properties["status"] = "In Progress"
        elif target_label == "Milestone":
            properties["deadline"] = "TBD"
            properties["status"] = "Pending"
        elif target_label == "Dataset":
            properties["source_type"] = "Ingested Data"
            properties["size"] = "1 Document"
        elif target_label == "Outcome":
            properties["description"] = clean_name
        elif target_label == "Deliverable":
            properties["type"] = "Artifact"
            properties["status"] = "Draft"

        return {
            "label": target_label,
            "pk_field": pk_field,
            "pk_val": canonical_id,
            "name": clean_name,
            "properties": properties
        }
