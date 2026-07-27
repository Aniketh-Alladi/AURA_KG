"""
Tests for mock data structure
"""

import pytest
import json
from components.api_handler import MockAPIHandler

class TestMockData:
    """Test suite for mock data"""
    
    def test_mock_data_structure(self):
        """Test mock data has correct structure"""
        handler = MockAPIHandler()
        result = handler.query_retrieval("test")
        
        # Check required fields
        assert "success" in result
        assert "answer" in result
        assert "supporting_nodes" in result
        assert "edges" in result
        
        # Check data types
        assert isinstance(result["supporting_nodes"], list)
        assert isinstance(result["edges"], list)
        
    def test_node_structure(self):
        """Test each node has required fields"""
        handler = MockAPIHandler()
        result = handler.query_retrieval("test")
        
        for node in result["supporting_nodes"]:
            assert "id" in node
            assert "type" in node
            assert "name" in node
            assert isinstance(node["id"], str)
            assert isinstance(node["type"], str)
            assert isinstance(node["name"], str)
    
    def test_edge_structure(self):
        """Test each edge has required fields"""
        handler = MockAPIHandler()
        result = handler.query_retrieval("test")
        
        for edge in result["edges"]:
            assert "source" in edge
            assert "target" in edge
            assert "relation" in edge
            assert isinstance(edge["source"], str)
            assert isinstance(edge["target"], str)
            assert isinstance(edge["relation"], str)
    
    def test_node_types_valid(self):
        """Test node types are valid"""
        valid_types = [
            "Person", "Project", "Domain", "Tool", "Feature",
            "Role", "Phase", "Milestone", "Outcome", "Deliverable", "Dataset"
        ]
        
        handler = MockAPIHandler()
        result = handler.query_retrieval("test")
        
        for node in result["supporting_nodes"]:
            assert node["type"] in valid_types
    
    def test_answer_not_empty(self):
        """Test answer is not empty"""
        handler = MockAPIHandler()
        result = handler.query_retrieval("test")
        
        assert len(result["answer"]) > 0
        assert isinstance(result["answer"], str)
    
    def test_mock_connection(self):
        """Test mock connection status"""
        handler = MockAPIHandler()
        result = handler.test_connection()
        
        assert result["status"] == "connected"
        assert "Mock API" in result["message"]
