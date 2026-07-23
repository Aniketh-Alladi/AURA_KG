"""
AURA-KG Named Entity Recognition (NER) Module.
Extracts entity mentions from unstructured text using spaCy (en_core_web_sm) with extensible architecture
designed for Transformer-based models in V2, plus fallback regex extraction if spaCy is missing.
"""

import abc
import re
import logging
from typing import Any, Dict, List, Optional

try:
    import spacy
    from spacy.language import Language
except ImportError:
    spacy = None
    Language = Any

logger = logging.getLogger(__name__)

# Known domain keywords for fallback extraction if spaCy is not installed
FALLBACK_KEYWORDS = [
    "Tejus", "Varun", "Aniketh", "Nikshith",
    "AURA-KG", "AURA", "Neo4j", "Docker", "spaCy", "Python", "Cypher",
    "Knowledge Graphs", "NLP", "Knowledge Graph Developer", "Data Ingestion",
    "LLM Developer", "Retrieval", "Frontend Developer", "Graph Design",
    "Knowledge Graph Storage", "Graph Query Engine"
]


class BaseNERExtractor(abc.ABC):
    """Abstract base class for NER Extractor implementations."""

    @abc.abstractmethod
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from input text.

        :param text: Raw text string.
        :return: List of entity dictionaries with text, label, start_char, end_char, and sentence.
        """
        pass


class SpacyNERExtractor(BaseNERExtractor):
    """spaCy-based Named Entity Extractor with fallback keyword extraction."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        """
        Initialize spaCy pipeline.

        :param model_name: Name of the spaCy model.
        """
        self.model_name = model_name
        self.nlp: Optional[Language] = None

        if spacy is not None:
            self._load_model()
        else:
            logger.warning(
                "spaCy is not installed in current environment. Using rule-based fallback entity extractor. "
                "To enable spaCy, run: pip install spacy && python -m spacy download %s",
                self.model_name
            )

    def _load_model(self) -> None:
        """Load the spaCy language model, downloading it dynamically if missing."""
        if spacy is None:
            return

        try:
            logger.info("Loading spaCy model '%s'...", self.model_name)
            self.nlp = spacy.load(self.model_name)
        except OSError:
            logger.warning("spaCy model '%s' not found locally. Attempting automatic download...", self.model_name)
            try:
                from spacy.cli import download
                download(self.model_name)
                self.nlp = spacy.load(self.model_name)
                logger.info("Successfully downloaded and loaded spaCy model '%s'.", self.model_name)
            except Exception as e:
                logger.error("Failed to download spaCy model '%s': %s", self.model_name, str(e))
                self.nlp = None

    def _extract_fallback_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback keyword entity extractor when spaCy is unavailable.

        :param text: Input text string.
        :return: List of entity dictionaries.
        """
        entities: List[Dict[str, Any]] = []

        # Split sentences roughly by punctuation
        sentences = [s.strip() for s in re.split(r"[.\n]+", text) if s.strip()]

        for sent in sentences:
            sent_offset = text.find(sent)
            for kw in FALLBACK_KEYWORDS:
                pattern = re.compile(r"\b" + re.escape(kw) + r"\b", re.I)
                for match in pattern.finditer(sent):
                    matched_text = match.group(0)
                    start_char = (sent_offset if sent_offset != -1 else 0) + match.start()
                    end_char = start_char + len(matched_text)

                    # Infer basic fallback label
                    if matched_text.lower() in ("tejus", "varun", "aniketh", "nikshith"):
                        label = "PERSON"
                    elif matched_text.lower() in ("neo4j", "docker", "spacy", "python", "cypher"):
                        label = "PRODUCT"
                    else:
                        label = "ORG"

                    entities.append({
                        "text": matched_text,
                        "spacy_label": label,
                        "start_char": start_char,
                        "end_char": end_char,
                        "sentence": sent,
                        "start_sent_idx": sent_offset if sent_offset != -1 else 0
                    })

        return entities

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities using spaCy NER or fallback rules.

        :param text: Cleaned raw text content.
        :return: List of entity dicts containing text, label, start_char, end_char, sentence text, and sentence index.
        """
        if not text or not text.strip():
            return []

        if self.nlp is None:
            return self._extract_fallback_entities(text)

        doc = self.nlp(text)
        entities: List[Dict[str, Any]] = []

        # Map entities and attach sentence context
        for ent in doc.ents:
            sent_text = ent.sent.text.strip() if ent.sent else ""
            sent_start = getattr(ent.sent, "start_char", 0) if ent.sent else 0

            entities.append({
                "text": ent.text.strip(),
                "spacy_label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "sentence": sent_text,
                "start_sent_idx": sent_start
            })

        logger.debug("Extracted %d entities from text length %d.", len(entities), len(text))
        return entities

# TODO V2: Implement TransformerNERExtractor(BaseNERExtractor) using HuggingFace / GLiNER / REBEL
