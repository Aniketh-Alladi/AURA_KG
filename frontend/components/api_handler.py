"""
API Handler for AURA-KG
Handles all communication with backend services
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class APIHandler:
    """Handles all API communication with the backend"""
    
    def __init__(self):
        """Initialize API handler with endpoints from environment"""
        self.retrieval_url = os.getenv('RETRIEVAL_API_URL', 'http://localhost:8000/api/v1/query')
        self.graph_url = os.getenv('GRAPH_API_URL', 'http://localhost:8000/api/graph')
        self.neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
        self.timeout = 30  # seconds
        
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the API
        
        Returns:
            Dict with connection status
        """
        try:
            health_url = self.retrieval_url.rsplit('/api/', 1)[0] + '/health'
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                return {"status": "connected", "message": "API is reachable"}
            else:
                return {"status": "error", "message": f"API returned status {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Cannot connect to API server"}
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Connection timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query_retrieval(self, query_text: str) -> Dict[str, Any]:
        """
        Send query to retrieval API
        
        Args:
            query_text: User's question
            
        Returns:
            Dict with answer and supporting graph data
        """
        try:
            # Prepare the request
            payload = {
                "query": query_text,
                "timestamp": datetime.now().isoformat()
            }
            
            # Make the API call
            response = requests.post(
                self.retrieval_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "answer": data.get("answer", "No answer found"),
                    "supporting_nodes": data.get("supporting_nodes", []),
                    "edges": data.get("edges", []),
                    "raw": data
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection Error",
                "details": "Cannot connect to the API server. Please check if it's running."
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout Error",
                "details": "Request timed out. The server might be busy."
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid Response",
                "details": "API returned invalid JSON"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Unexpected Error",
                "details": str(e)
            }
    
    def get_graph_data(self, node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch graph data from the API
        
        Args:
            node_ids: Optional list of node IDs to filter
            
        Returns:
            Dict with nodes and edges
        """
        try:
            payload = {"node_ids": node_ids} if node_ids else {}
            
            response = requests.post(
                self.graph_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "nodes": data.get("nodes", []),
                    "edges": data.get("edges", []),
                    "raw": data
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection Error",
                "details": "Cannot connect to the API server"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout Error",
                "details": "Request timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Unexpected Error",
                "details": str(e)
            }
    
    def get_node_details(self, node_id: str) -> Dict[str, Any]:
        """
        Get details for a specific node
        
        Args:
            node_id: ID of the node
            
        Returns:
            Dict with node details
        """
        try:
            response = requests.get(
                f"{self.graph_url}/node/{node_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "node": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_nodes(self, search_term: str, node_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for nodes by name or property
        
        Args:
            search_term: Text to search for
            node_type: Optional filter by node type
            
        Returns:
            Dict with search results
        """
        try:
            params = {"q": search_term}
            if node_type:
                params["type"] = node_type
                
            response = requests.get(
                f"{self.graph_url}/search",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "results": response.json().get("results", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class MockAPIHandler(APIHandler):
    """Mock API handler for testing without backend"""
    
    def __init__(self):
        super().__init__()
        self.use_mock = True
    
    def query_retrieval(self, query_text: str) -> Dict[str, Any]:
        """Mock query retrieval"""
        # Generate mock response based on query
        mock_response = {
            "success": True,
            "answer": f"Based on your knowledge graph about '{query_text}':\n\n"
                      f"The AURA-KG project involves multiple team members working on knowledge graph systems. "
                      f"Key technologies include Neo4j for graph storage and Streamlit for the frontend.",
            "supporting_nodes": [
                {"type": "Project", "id": "proj_001", "name": "AURA-KG"},
                {"type": "Person", "id": "person_001", "name": "Nikshith"},
                {"type": "Person", "id": "person_002", "name": "Tejus"},
                {"type": "Person", "id": "person_003", "name": "Aniketh"},
                {"type": "Tool", "id": "tool_001", "name": "Neo4j"},
                {"type": "Tool", "id": "tool_002", "name": "Streamlit"},
                {"type": "Tool", "id": "tool_003", "name": "Python"},
                {"type": "Domain", "id": "domain_001", "name": "Machine Learning"},
                {"type": "Domain", "id": "domain_002", "name": "Data Science"},
                {"type": "Feature", "id": "feature_001", "name": "Graph Queries"},
                {"type": "Feature", "id": "feature_002", "name": "Visualization"}
            ],
            "edges": [
                {"source": "person_001", "target": "proj_001", "relation": "works_on"},
                {"source": "person_002", "target": "proj_001", "relation": "works_on"},
                {"source": "person_003", "target": "proj_001", "relation": "works_on"},
                {"source": "proj_001", "target": "tool_001", "relation": "uses"},
                {"source": "proj_001", "target": "tool_002", "relation": "uses"},
                {"source": "proj_001", "target": "tool_003", "relation": "uses"},
                {"source": "proj_001", "target": "domain_001", "relation": "involves"},
                {"source": "proj_001", "target": "domain_002", "relation": "involves"},
                {"source": "tool_001", "target": "feature_001", "relation": "enables"},
                {"source": "tool_002", "target": "feature_002", "relation": "enables"}
            ]
        }
        return mock_response
    
    def test_connection(self) -> Dict[str, Any]:
        """Mock connection test"""
        return {"status": "connected", "message": "Mock API is ready"}


def get_api_handler(use_mock: bool = False) -> APIHandler:
    """
    Factory function to get API handler
    
    Args:
        use_mock: If True, use mock handler
        
    Returns:
        APIHandler instance
    """
    if use_mock:
        return MockAPIHandler()
    return APIHandler()