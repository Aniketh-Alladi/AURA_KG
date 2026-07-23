"""
AURA-KG Document Loader Module.
Loads normalized ingestion JSON documents produced by the data ingestion pipeline.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

REQUIRED_DOCUMENT_KEYS = {"source_type", "source_path", "raw_text", "metadata"}

class DocumentLoader:
    """Loader and validator for normalized document payloads."""

    def __init__(self, data_path: Union[str, Path]) -> None:
        """
        Initialize DocumentLoader with target directory or single JSON file path.

        :param data_path: Path to directory containing .json document files or single .json payload file.
        """
        self.data_path = Path(data_path)

    def validate_document(self, doc: Dict[str, Any], file_ref: str) -> bool:
        """
        Validate that a document dictionary conforms to the required ingestion contract.

        :param doc: Document dictionary to validate.
        :param file_ref: Reference string (filename or index) for logging.
        :return: True if valid, False otherwise.
        """
        if not isinstance(doc, dict):
            logger.error("Document in '%s' is not a valid JSON object.", file_ref)
            return False

        missing_keys = REQUIRED_DOCUMENT_KEYS - doc.keys()
        if missing_keys:
            logger.error("Document in '%s' missing required keys: %s", file_ref, missing_keys)
            return False

        if not isinstance(doc.get("metadata"), dict):
            logger.error("Document metadata in '%s' is not a dictionary.", file_ref)
            return False

        return True

    def load(self) -> List[Dict[str, Any]]:
        """
        Load and validate documents from the specified path.

        :return: List of validated normalized document dictionaries.
        """
        documents: List[Dict[str, Any]] = []

        if not self.data_path.exists():
            logger.error("Data path does not exist: %s", self.data_path)
            raise FileNotFoundError(f"Data path not found: {self.data_path}")

        if self.data_path.is_file():
            logger.info("Loading documents from single file: %s", self.data_path)
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    content = json.load(f)

                if isinstance(content, list):
                    for idx, item in enumerate(content):
                        if self.validate_document(item, f"{self.data_path.name}[{idx}]"):
                            documents.append(item)
                elif isinstance(content, dict):
                    if self.validate_document(content, self.data_path.name):
                        documents.append(content)
                else:
                    logger.error("File '%s' contains neither a JSON object nor array.", self.data_path.name)
            except json.JSONDecodeError as e:
                logger.error("Malformed JSON file '%s': %s", self.data_path.name, str(e))
            except Exception as e:
                logger.error("Error reading file '%s': %s", self.data_path.name, str(e))

        elif self.data_path.is_dir():
            logger.info("Scanning directory for JSON documents: %s", self.data_path)
            json_files = sorted(list(self.data_path.glob("*.json")))

            for json_file in json_files:
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        content = json.load(f)

                    if isinstance(content, list):
                        for idx, item in enumerate(content):
                            if self.validate_document(item, f"{json_file.name}[{idx}]"):
                                documents.append(item)
                    elif isinstance(content, dict):
                        if self.validate_document(content, json_file.name):
                            documents.append(content)
                except json.JSONDecodeError as e:
                    logger.error("Skipping malformed JSON file '%s': %s", json_file.name, str(e))
                except Exception as e:
                    logger.error("Failed to read document '%s': %s", json_file.name, str(e))

        logger.info("Successfully loaded %d document(s).", len(documents))
        return documents


def load_documents(data_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Convenience function to load normalized document payloads.

    :param data_path: Path to input file or directory.
    :return: List of normalized document dictionaries.
    """
    loader = DocumentLoader(data_path)
    return loader.load()
