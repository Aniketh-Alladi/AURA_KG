"""
Unit tests for Dashboard Components
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from components.dashboard import (
    render_metrics,
    render_node_distribution,
    render_query_activity,
    render_node_type_progress,
    render_graph_statistics,
    render_recent_queries,
    render_performance_metrics,
    render_export_options
)

class TestDashboardComponents:
    """Test suite for Dashboard components"""
    
    def test_render_metrics_with_data(self):
        """Test metrics rendering with data"""
        graph_data = {
            "nodes": [
                {"type": "Person", "id": "p1", "name": "Test"},
                {"type": "Project", "id": "pr1", "name": "Project"}
            ],
            "edges": [
                {"source": "p1", "target": "pr1", "relation": "works_on"}
            ]
        }
        query_history = [
            {"query": "test1", "timestamp": "12:00"},
            {"query": "test2", "timestamp": "12:01"}
        ]
        
        result = render_metrics(graph_data, query_history)
        assert result is not None
        assert "Person" in result
        assert "Project" in result
        assert result["Person"] == 1
    
    def test_render_metrics_empty(self):
        """Test metrics rendering with empty data"""
        result = render_metrics(None, [])
        assert result == {}
    
    def test_node_distribution_with_data(self):
        """Test node distribution rendering"""
        node_types = {
            "Person": 3,
            "Project": 2,
            "Tool": 4
        }
        result = render_node_distribution(node_types)
        assert result is None
    
    def test_node_distribution_empty(self):
        """Test node distribution with empty data"""
        result = render_node_distribution({})
        assert result is None
    
    def test_query_activity_with_history(self):
        """Test query activity chart"""
        query_history = [
            {"query": "test1", "timestamp": "12:00", "date": "2024-01-01"},
            {"query": "test2", "timestamp": "12:01", "date": "2024-01-01"}
        ]
        result = render_query_activity(query_history)
        assert result is None
    
    def test_query_activity_empty(self):
        """Test query activity with empty history"""
        result = render_query_activity([])
        assert result is None
    
    def test_node_type_progress(self):
        """Test node type progress bars"""
        node_types = {"Person": 5, "Project": 3, "Tool": 2}
        total_nodes = 10
        result = render_node_type_progress(node_types, total_nodes)
        assert result is None
    
    def test_node_type_progress_empty(self):
        """Test node type progress with empty data"""
        result = render_node_type_progress({}, 0)
        assert result is None
    
    def test_graph_statistics_with_data(self):
        """Test graph statistics rendering"""
        graph_data = {
            "nodes": [
                {"id": "n1"}, {"id": "n2"}, {"id": "n3"}
            ],
            "edges": [
                {"source": "n1", "target": "n2"},
                {"source": "n2", "target": "n3"}
            ]
        }
        result = render_graph_statistics(graph_data)
        assert result is None
    
    def test_graph_statistics_empty(self):
        """Test graph statistics with empty data"""
        result = render_graph_statistics(None)
        assert result is None
    
    def test_recent_queries_with_data(self):
        """Test recent queries table"""
        query_history = [
            {"query": "test1", "timestamp": "12:00"},
            {"query": "test2", "timestamp": "12:01"},
            {"query": "test3", "timestamp": "12:02"}
        ]
        result = render_recent_queries(query_history)
        assert result is None
    
    def test_recent_queries_empty(self):
        """Test recent queries with empty history"""
        result = render_recent_queries([])
        assert result is None
    
    def test_performance_metrics(self):
        """Test performance metrics rendering"""
        result = render_performance_metrics()
        assert result is None
    
    def test_export_options(self):
        """Test export options rendering"""
        query_history = [
            {"query": "test", "timestamp": "12:00"}
        ]
        graph_data = {"nodes": [], "edges": []}
        result = render_export_options(query_history, graph_data)
        assert result is None
