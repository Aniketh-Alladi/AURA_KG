"""
Pytest configuration and fixtures
"""

import pytest
import json
from unittest.mock import Mock
from components.api_handler import MockAPIHandler

@pytest.fixture
def mock_api_handler():
    """Provide a mock API handler for tests"""
    return MockAPIHandler()

@pytest.fixture
def sample_graph_data():
    """Provide sample graph data for tests"""
    return {
        "nodes": [
            {"id": "n1", "type": "Person", "name": "Test Person"},
            {"id": "n2", "type": "Project", "name": "Test Project"},
            {"id": "n3", "type": "Tool", "name": "Test Tool"}
        ],
        "edges": [
            {"source": "n1", "target": "n2", "relation": "works_on"},
            {"source": "n2", "target": "n3", "relation": "uses"}
        ]
    }

@pytest.fixture
def sample_query_history():
    """Provide sample query history for tests"""
    return [
        {"query": "What is AURA-KG?", "timestamp": "10:00", "date": "2024-01-01"},
        {"query": "Show me connections", "timestamp": "10:30", "date": "2024-01-01"},
        {"query": "Who is working on frontend?", "timestamp": "11:00", "date": "2024-01-01"}
    ]
