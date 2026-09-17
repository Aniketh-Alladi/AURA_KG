import streamlit as st
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv
from components.api_handler import get_api_handler, APIHandler
import os
import time

# Load environment variables
load_dotenv()

# Page configuration - MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="AURA-KG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    try:
        with open('static/css/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styles.")

load_css()

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = None
if 'current_graph_data' not in st.session_state:
    st.session_state.current_graph_data = None
if 'search_triggered' not in st.session_state:
    st.session_state.search_triggered = False
if 'query_text' not in st.session_state:
    st.session_state.query_text = ""

# Initialize API handler
if 'api_handler' not in st.session_state:
    # Talk to the real retrieval API; individual queries fall back to mock data on failure.
    st.session_state.api_handler = get_api_handler(use_mock=False)

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("", ["🔍 Query", "🌐 Graph Explorer", "📊 Dashboard"])
    
    st.markdown("---")
    st.markdown("### Status")
    st.success("🟢 System Online")
    st.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Show API status
    st.markdown("---")
    st.markdown("### Configuration")
    api_status = "✅" if os.getenv('RETRIEVAL_API_URL') else "❌"
    st.write(f"API Config: {api_status}")

# Main content
if page == "🔍 Query":
    st.markdown('<p class="main-header">🔍 Query Your Knowledge Graph</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about your personal knowledge base</p>', unsafe_allow_html=True)
    
    # Query input
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            query = st.text_input(
                "Enter your question:",
                placeholder="What did I learn about project X last month?",
                label_visibility="collapsed",
                key="query_input"
            )
        with col2:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Example queries
    with st.expander("💡 Example Queries"):
        example_queries = [
            "What are the key milestones for our AI project?",
            "Show me connections between machine learning and data science",
            "Who are the team members working on the frontend?"
        ]
        for q in example_queries:
            if st.button(q, key=f"example_{q[:20]}"):
                # Store the query in session state and trigger search
                st.session_state.query_text = q
                st.session_state.search_triggered = True
    
    # Check if we need to trigger a search from example button
    if st.session_state.search_triggered and st.session_state.query_text:
        query = st.session_state.query_text
        # Reset the trigger
        st.session_state.search_triggered = False
        # Force the search
        search_clicked = True
    
    # Process search
    if search_clicked and query:
        with st.spinner("🧠 Retrieving answer from your knowledge graph..."):
            # Try real API
            response = st.session_state.api_handler.query_retrieval(query)
            
            if response.get("success", False):
                # Success - use real API response
                st.session_state.current_answer = response.get("answer", "No answer found")
                st.session_state.current_graph_data = {
                    "nodes": response.get("supporting_nodes", []),
                    "edges": response.get("edges", [])
                }
                st.success("✅ Retrieved from knowledge graph!")
            else:
                # API error - show error and fallback to mock
                error_msg = response.get("error", "Unknown error")
                st.warning(f"⚠️ API Error: {error_msg}. Using fallback mock data.")
                
                # Fallback to mock data
                mock_api = get_api_handler(use_mock=True)
                mock_response = mock_api.query_retrieval(query)
                
                st.session_state.current_answer = mock_response.get("answer", "No answer found")
                st.session_state.current_graph_data = {
                    "nodes": mock_response.get("supporting_nodes", []),
                    "edges": mock_response.get("edges", [])
                }
            
            # Add to history
            st.session_state.query_history.append({
                "query": query,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "status": "success" if response.get("success", False) else "fallback"
            })

    
    # Display answer if available
    if st.session_state.current_answer:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 💬 Answer")
            st.markdown(f'<div class="answer-box">{st.session_state.current_answer}</div>', 
                       unsafe_allow_html=True)
            
            with st.expander("📚 Supporting Sources"):
                if st.session_state.current_graph_data:
                    for node in st.session_state.current_graph_data["nodes"]:
                        st.markdown(f'🔹 <strong>{node["name"]}</strong> ({node["type"]})', 
                                  unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 Context")
            if st.session_state.current_graph_data:
                nodes = st.session_state.current_graph_data["nodes"]
                edges = st.session_state.current_graph_data["edges"]
                st.metric("Total Nodes", len(nodes))
                st.metric("Total Relations", len(edges))
                
                # Show node types breakdown
                node_types = {}
                for node in nodes:
                    node_types[node["type"]] = node_types.get(node["type"], 0) + 1
                st.write("**Node Types:**")
                for ntype, count in node_types.items():
                    st.write(f"- {ntype}: {count}")
    
    # Query History
    if st.session_state.query_history:
        with st.expander("📜 Query History"):
            history_df = pd.DataFrame(st.session_state.query_history)
            st.dataframe(
                history_df[["timestamp", "query"]],
                use_container_width=True,
                hide_index=True
            )

elif page == "🌐 Graph Explorer":
    st.markdown('<p class="main-header">🌐 Graph Explorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore connections in your knowledge graph</p>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        node_types = ["Person", "Project", "Domain", "Tool", "Feature"]
        selected_types = st.multiselect(
            "Filter by node type:",
            node_types,
            default=node_types
        )
    with col2:
        max_nodes = st.slider("Maximum nodes to display:", 5, 50, 20)
    
    if st.session_state.current_graph_data:
        graph_data = st.session_state.current_graph_data
        
        # Filter nodes by type
        filtered_nodes = [n for n in graph_data["nodes"] if n["type"] in selected_types]
        
        # Limit nodes if needed
        if len(filtered_nodes) > max_nodes:
            filtered_nodes = filtered_nodes[:max_nodes]
        
        # Filter edges to only include filtered nodes
        filtered_node_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [
            e for e in graph_data["edges"] 
            if e["source"] in filtered_node_ids and e["target"] in filtered_node_ids
        ]
        
        st.markdown(f"### 📊 Showing {len(filtered_nodes)} nodes and {len(filtered_edges)} edges")
        
        # Cytoscape.js HTML
        cytoscape_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
            <style>
                #cy {{
                    width: 100%;
                    height: 600px;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }}
                #cy-info {{
                    position: absolute;
                    bottom: 10px;
                    left: 10px;
                    background: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    font-size: 12px;
                    color: #555;
                    pointer-events: none;
                }}
            </style>
        </head>
        <body>
            <div style="position:relative;">
                <div id="cy"></div>
                <div id="cy-info">Click on a node to see details</div>
            </div>
            <script>
                const nodes = {json.dumps(filtered_nodes)};
                const edges = {json.dumps(filtered_edges)};
                
                const colors = {{
                    'Person': '#3498DB',
                    'Role': '#2ECC71',
                    'Project': '#E74C3C',
                    'Domain': '#F39C12',
                    'Tool': '#9B59B6',
                    'Feature': '#1ABC9C',
                    'Phase': '#E67E22',
                    'Milestone': '#2C3E50',
                    'Outcome': '#27AE60',
                    'Deliverable': '#2980B9',
                    'Dataset': '#8E44AD'
                }};
                
                const elements = [
                    ...nodes.map(n => ({{
                        data: {{
                            id: n.id,
                            label: n.name,
                            type: n.type
                        }},
                        style: {{
                            'background-color': colors[n.type] || '#95A5A6'
                        }}
                    }})),
                    ...edges.map(e => ({{
                        data: {{
                            id: e.source + '-' + e.target,
                            source: e.source,
                            target: e.target,
                            label: e.relation
                        }}
                    }}))
                ];
                
                const cy = cytoscape({{
                    container: document.getElementById('cy'),
                    elements: elements,
                    style: [
                        {{
                            selector: 'node',
                            style: {{
                                'label': 'data(label)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'color': '#fff',
                                'font-size': '12px',
                                'font-weight': 'bold',
                                'width': '60px',
                                'height': '60px',
                                'border-width': 2,
                                'border-color': '#2C3E50'
                            }}
                        }},
                        {{
                            selector: 'edge',
                            style: {{
                                'label': 'data(label)',
                                'font-size': '10px',
                                'text-rotation': 'autorotate',
                                'width': 2,
                                'line-color': '#7F8C8D',
                                'target-arrow-color': '#7F8C8D',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier'
                            }}
                        }}
                    ],
                    layout: {{
                        name: 'cose',
                        idealEdgeLength: 100,
                        nodeRepulsion: 400000,
                        edgeElasticity: 100,
                        nestingFactor: 5,
                        gravity: 80,
                        numIter: 1000,
                        initialTemp: 200,
                        coolingFactor: 0.95,
                        minTemp: 1.0
                    }}
                }});
                
                // Click handler
                cy.on('tap', 'node', function(evt) {{
                    const node = evt.target;
                    const data = node.data();
                    alert(`Node: ${{data.label}}\\nType: ${{data.type}}\\nID: ${{data.id}}`);
                }});
                
                // Hover effect
                cy.on('mouseover', 'node', function(evt) {{
                    const node = evt.target;
                    node.style('border-width', '4px');
                    node.style('border-color', '#FFD700');
                }});
                
                cy.on('mouseout', 'node', function(evt) {{
                    const node = evt.target;
                    node.style('border-width', '2px');
                    node.style('border-color', '#2C3E50');
                }});
                
                // Fit graph to viewport
                cy.fit();
            </script>
        </body>
        </html>
        """
        st.components.v1.html(cytoscape_html, height=650)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Nodes", len(filtered_nodes))
        with col2:
            st.metric("🔗 Edges", len(filtered_edges))
        with col3:
            unique_types = len(set(n["type"] for n in filtered_nodes))
            st.metric("🏷️ Node Types", unique_types)
    else:
        st.info("💡 No graph data available. Go to the Query page to generate a graph.")

else:  # Dashboard
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
    
    st.markdown('<p class="main-header">📊 Knowledge Graph Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Overview of your personal knowledge management system</p>', unsafe_allow_html=True)
    
    # Render metrics
    node_types = render_metrics(st.session_state.current_graph_data, st.session_state.query_history)
    
    # Determine data availability
    has_graph_data = st.session_state.current_graph_data is not None
    total_nodes = len(st.session_state.current_graph_data["nodes"]) if has_graph_data else 0
    
    st.markdown("---")
    
    # Interactive Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Node Type Distribution")
        render_node_distribution(node_types)
    
    with col2:
        st.markdown("### 📈 Query Activity")
        render_query_activity(st.session_state.query_history)
    
    # Third Row: Advanced Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔥 Most Common Node Types")
        render_node_type_progress(node_types, total_nodes)
    
    with col2:
        st.markdown("### 📋 Recent Queries")
        render_recent_queries(st.session_state.query_history)
    
    with col3:
        st.markdown("### 📊 Graph Statistics")
        render_graph_statistics(st.session_state.current_graph_data)
    
    # Fourth Row: Performance Metrics
    st.markdown("---")
    st.markdown("### ⚡ System Performance")
    render_performance_metrics()
    
    # Fifth Row: Export Options
    st.markdown("---")
    st.markdown("### 📤 Export Options")
    render_export_options(st.session_state.query_history, st.session_state.current_graph_data)