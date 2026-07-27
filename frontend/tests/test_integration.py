"""
Integration tests for AURA-KG frontend
"""

import pytest
import json
from unittest.mock import Mock, patch
from components.api_handler import get_api_handler, MockAPIHandler

class TestIntegration:
    """Integration test suite"""
    
    @patch('components.api_handler.requests.post')
    def test_api_fallback_mechanism(self, mock_post):
        """Test fallback mechanism when API fails"""
        mock_post.side_effect = Exception("Connection failed")
        
        handler = get_api_handler(use_mock=False)
        result = handler.query_retrieval("test query")
        
        assert result["success"] is False
        assert "error" in result
        
        mock_handler = get_api_handler(use_mock=True)
        mock_result = mock_handler.query_retrieval("test query")
        assert mock_result["success"] is True
    
    @patch('components.api_handler.requests.post')
    def test_api_success_path(self, mock_post):
        """Test successful API path"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "answer": "Test answer from API",
            "supporting_nodes": [
                {"id": "n1", "type": "Test", "name": "Test Node"}
            ],
            "edges": []
        }
        mock_post.return_value = mock_response
        
        handler = get_api_handler(use_mock=False)
        result = handler.query_retrieval("test query")
        
        assert result["success"] is True
        assert result["answer"] == "Test answer from API"
    
    def test_session_state_mock(self):
        """Test session state with mock API"""
        api_handler = get_api_handler(use_mock=True)
        assert isinstance(api_handler, MockAPIHandler)
        assert api_handler.use_mock is True
        
        result = api_handler.query_retrieval("test")
        assert result["success"] is True
        assert len(result["supporting_nodes"]) > 0
        assert len(result["edges"]) > 0
    
    def test_data_consistency(self):
        """Test data consistency between different calls"""
        handler = get_api_handler(use_mock=True)
        
        results = []
        for i in range(3):
            result = handler.query_retrieval(f"test query {i}")
            results.append(result)
        
        for r in results:
            assert r["success"] is True
            assert "supporting_nodes" in r
            assert "edges" in r
            assert isinstance(r["supporting_nodes"], list)
            assert isinstance(r["edges"], list)
