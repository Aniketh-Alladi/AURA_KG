"""
Unit tests for API Handler
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from components.api_handler import APIHandler, MockAPIHandler, get_api_handler

class TestAPIHandler:
    """Test suite for API Handler"""
    
    def test_init(self):
        """Test API handler initialization"""
        handler = APIHandler()
        assert handler.retrieval_url == 'http://localhost:8000/api/retrieve'
        assert handler.graph_url == 'http://localhost:8000/api/graph'
        assert handler.timeout == 30
    
    def test_mock_init(self):
        """Test Mock API handler initialization"""
        handler = MockAPIHandler()
        assert handler.use_mock is True
    
    @patch('components.api_handler.requests.post')
    def test_query_retrieval_success(self, mock_post):
        """Test successful query retrieval"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answer": "Test answer",
            "supporting_nodes": [{"id": "n1", "type": "Test", "name": "Node 1"}],
            "edges": [{"source": "n1", "target": "n2", "relation": "test"}]
        }
        mock_post.return_value = mock_response
        
        handler = APIHandler()
        result = handler.query_retrieval("test query")
        
        assert result["success"] is True
        assert result["answer"] == "Test answer"
        assert len(result["supporting_nodes"]) == 1
        
    @patch('components.api_handler.requests.post')
    def test_query_retrieval_error(self, mock_post):
        """Test query retrieval with API error"""
        mock_post.side_effect = Exception("Connection error")
        
        handler = APIHandler()
        result = handler.query_retrieval("test query")
        
        assert result["success"] is False
        assert "error" in result
        
    def test_mock_query_retrieval(self):
        """Test mock query retrieval"""
        handler = MockAPIHandler()
        result = handler.query_retrieval("test query")
        
        assert result["success"] is True
        assert "answer" in result
        assert "supporting_nodes" in result
        assert "edges" in result
        assert len(result["supporting_nodes"]) > 0
    
    @patch('components.api_handler.requests.post')
    def test_get_graph_data_success(self, mock_post):
        """Test successful graph data retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "nodes": [{"id": "n1", "type": "Test"}],
            "edges": [{"source": "n1", "target": "n2"}]
        }
        mock_post.return_value = mock_response
        
        handler = APIHandler()
        result = handler.get_graph_data()
        
        assert result["success"] is True
        assert "nodes" in result
    
    @patch('components.api_handler.requests.post')
    def test_get_graph_data_error(self, mock_post):
        """Test graph data retrieval with error"""
        mock_post.side_effect = Exception("Connection error")
        
        handler = APIHandler()
        result = handler.get_graph_data()
        
        assert result["success"] is False
        assert "error" in result
    
    def test_get_api_handler_mock(self):
        """Test get_api_handler factory with mock"""
        handler = get_api_handler(use_mock=True)
        assert isinstance(handler, MockAPIHandler)
    
    def test_get_api_handler_real(self):
        """Test get_api_handler factory with real"""
        handler = get_api_handler(use_mock=False)
        assert isinstance(handler, APIHandler)
