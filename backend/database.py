"""
AURA-KG Neo4j Database Connection Manager.
Handles connection lifecycle, sessions, and transaction execution using official Neo4j Python driver.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator
from neo4j import GraphDatabase, Driver, ManagedTransaction, Session

from backend.config import Config

logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """Thread-safe manager for Neo4j database driver connection and execution."""

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None
    ) -> None:
        """Initialize Neo4j database configuration."""
        self.uri = uri or getattr(Config, "NEO4J_URI", "neo4j://localhost:7687")
        self.user = user or getattr(Config, "NEO4J_USER", "neo4j")
        self.password = password or getattr(Config, "NEO4J_PASSWORD", "password")
        self.database = database or getattr(Config, "NEO4J_DATABASE", "neo4j")
        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        """Establish database driver connection if not already connected."""
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password)
                )
                logger.info("Connected to Neo4j database at %s", self.uri)
            except Exception as e:
                logger.error("Failed to connect to Neo4j database: %s", str(e))
                raise
        return self._driver

    def verify_connectivity(self) -> bool:
        """Verify database driver connectivity."""
        try:
            driver = self.connect()
            driver.verify_connectivity()
            logger.info("Neo4j connectivity check passed.")
            return True
        except Exception as e:
            logger.warning("Neo4j connectivity check failed: %s", str(e))
            return False

    def close(self) -> None:
        """Close Neo4j driver connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Closed Neo4j database connection.")

    def execute_write(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute write Cypher query in a transaction."""
        driver = self.connect()
        parameters = parameters or {}

        def _work(tx: ManagedTransaction):
            result = tx.run(cypher, parameters)
            return [record.data() for record in result]

        with driver.session(database=self.database) as session:
            return session.execute_write(_work)

    def execute_read(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute read Cypher query in a transaction."""
        driver = self.connect()
        parameters = parameters or {}

        def _work(tx: ManagedTransaction):
            result = tx.run(cypher, parameters)
            return [record.data() for record in result]

        with driver.session(database=self.database) as session:
            return session.execute_read(_work)

    def get_session(self) -> Session:
        """Helper to obtain a direct session instance."""
        driver = self.connect()
        return driver.session(database=self.database)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Instantiate a default singleton instance for module-level convenience
db = Neo4jDatabase()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Module-level context manager for yielding a database session.
    Maintains compatibility with direct `with get_session() as session:` calls across the backend.
    """
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()