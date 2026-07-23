"""
AURA-KG Backend Configuration Module.
Provides centralized access to environment variables and configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Config:
    """Central configuration class for AURA-KG backend services."""

    # Neo4j Settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password123")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # NLP & Extraction Settings
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")

    # Pipeline Data Paths
    DEFAULT_DATA_DIR: Path = BASE_DIR.parent / "dummy_data"
    DEFAULT_INPUT_FILE: Path = BASE_DIR.parent / "normalized_ingestion_output.json"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
