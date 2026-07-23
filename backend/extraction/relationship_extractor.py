"""
AURA-KG Relationship Extractor Module.
Extracts semantic relationships between classified entities at sentence/document level using pattern matching,
co-occurrence rules, and schema domain constraints.
"""

import re
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Valid Schema Relationship Triplets: (Source Label, Target Label) -> Relationship Type
SCHEMA_RELATIONSHIP_RULES: Dict[Tuple[str, str], str] = {
    ("Person", "Role"): "ASSIGNED_TO",
    ("Role", "Project"): "ASSIGNED_TO",
    ("Role", "Role"): "DEPENDS_ON",
    ("Project", "Feature"): "HAS_FEATURE",
    ("Project", "Phase"): "HAS_PHASE",
    ("Phase", "Milestone"): "HAS_DEADLINE",
    ("Project", "Deliverable"): "HAS_DELIVERABLE",
    ("Project", "Tool"): "USES_TOOL",
    ("Tool", "Feature"): "SERVES_PURPOSE",
    ("Project", "Domain"): "BELONGS_TO_DOMAIN",
    ("Person", "Outcome"): "GAINED",
    ("Dataset", "Phase"): "USED_IN",
}

# Regex Pattern Rules for Text Clues
TEXT_RELATIONSHIP_PATTERNS = [
    (re.compile(r"\b(assigned to|working as|role is|lead)\b", re.I), "ASSIGNED_TO"),
    (re.compile(r"\b(depends on|requires|prerequisite)\b", re.I), "DEPENDS_ON"),
    (re.compile(r"\b(uses|built with|powered by|developed using|tech stack|using)\b", re.I), "USES_TOOL"),
    (re.compile(r"\b(serves|supports|purpose of|enables)\b", re.I), "SERVES_PURPOSE"),
    (re.compile(r"\b(has feature|includes feature|contains|feature)\b", re.I), "HAS_FEATURE"),
    (re.compile(r"\b(divided into|phase|stage)\b", re.I), "HAS_PHASE"),
    (re.compile(r"\b(deadline|milestone|target date|due)\b", re.I), "HAS_DEADLINE"),
    (re.compile(r"\b(belongs to|domain|field of)\b", re.I), "BELONGS_TO_DOMAIN"),
    (re.compile(r"\b(produces|delivers|deliverable|output)\b", re.I), "HAS_DELIVERABLE"),
    (re.compile(r"\b(used in|utilized during|processed during)\b", re.I), "USED_IN"),
    (re.compile(r"\b(gained|learned|achieved|outcome)\b", re.I), "GAINED"),
]


class RelationshipExtractor:
    """Extracts schema-compliant relationships between classified nodes."""

    def __init__(self) -> None:
        """Initialize relationship rules and text triggers."""
        self.schema_rules = SCHEMA_RELATIONSHIP_RULES
        self.text_patterns = TEXT_RELATIONSHIP_PATTERNS

    def _infer_relationship_type(
        self, source_label: str, target_label: str, sentence: str
    ) -> str:
        """
        Infer relationship type between two node types based on text patterns or schema defaults.

        :param source_label: Source node label.
        :param target_label: Target node label.
        :param sentence: Sentence context text.
        :return: String relationship type.
        """
        # Check text patterns first
        for pattern, rel_type in self.text_patterns:
            if pattern.search(sentence):
                # Verify schema validity
                expected_rel = self.schema_rules.get((source_label, target_label))
                if expected_rel == rel_type:
                    return rel_type

        # Fallback to schema default for the entity pair
        return self.schema_rules.get((source_label, target_label), "")

    def extract_relationships(
        self, sentence: str, classified_nodes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract pairwise relationships between classified nodes occurring in the same sentence.

        :param sentence: Sentence text string.
        :param classified_nodes: List of classified node dictionaries present in sentence.
        :return: List of relationship dictionaries.
        """
        relationships: List[Dict[str, Any]] = []

        if len(classified_nodes) < 2:
            return relationships

        # Pairwise candidate search within the sentence
        for i in range(len(classified_nodes)):
            for j in range(len(classified_nodes)):
                if i == j:
                    continue

                source_node = classified_nodes[i]
                target_node = classified_nodes[j]

                # Do not link identical node IDs
                if source_node["pk_val"] == target_node["pk_val"]:
                    continue

                source_label = source_node["label"]
                target_label = target_node["label"]

                rel_type = self._infer_relationship_type(source_label, target_label, sentence)

                if rel_type:
                    rel_dict = {
                        "source_label": source_label,
                        "source_pk_field": source_node["pk_field"],
                        "source_pk_val": source_node["pk_val"],
                        "target_label": target_label,
                        "target_pk_field": target_node["pk_field"],
                        "target_pk_val": target_node["pk_val"],
                        "rel_type": rel_type,
                        "sentence": sentence
                    }

                    # Prevent duplicate relationship records
                    if rel_dict not in relationships:
                        relationships.append(rel_dict)
                        logger.debug(
                            "Extracted relationship: (%s:%s) -[:%s]-> (%s:%s)",
                            source_label, source_node["pk_val"],
                            rel_type,
                            target_label, target_node["pk_val"]
                        )

        return relationships

# TODO V2: Transformer-based Relationship Extraction
# Replace/augment rule-based relationship extraction with zero-shot RE models (e.g. REBEL, OpenIE, or LLM-based extraction).
