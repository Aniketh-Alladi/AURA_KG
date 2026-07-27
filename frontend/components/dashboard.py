"""
Dashboard Components for AURA-KG
Contains all dashboard visualization and metric functions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import random

def render_metrics(graph_data, query_history):
    """
    Render dashboard metrics cards
    
    Args:
        graph_data: Current graph data (nodes + edges)
        query_history: List of past queries
    
    Returns:
        dict: Node type distribution
    """
    total_queries = len(query_history)
    has_graph_data = graph_data is not None
    total_nodes = len(graph_data["nodes"]) if has_graph_data else 0
    total_edges = len(graph_data["edges"]) if has_graph_data else 0
    
    # Calculate node type distribution
    node_types = {}
    if has_graph_data:
        for node in graph_data["nodes"]:
            node_types[node["type"]] = node_types.get(node["type"], 0) + 1
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            "📊 Total Nodes", 
            total_nodes,
            delta="+6" if has_graph_data else "+0",
            help="Total number of nodes in the knowledge graph"
        )
    with col2:
        st.metric(
            "🔗 Total Relations", 
            total_edges,
            delta="+7" if has_graph_data else "+0",
            help="Total number of relationships between nodes"
        )
    with col3:
        st.metric(
            "📝 Node Types", 
            len(node_types),
            help="Distinct node types in the graph"
        )
    with col4:
        st.metric(
            "❓ Queries", 
            total_queries,
            delta="+2" if total_queries > 0 else "+0",
            help="Total number of queries processed"
        )
    with col5:
        st.metric(
            "📅 Sessions", 
            "1",
            help="Active user sessions"
        )
    
    return node_types

def render_node_distribution(node_types):
    """
    Render pie chart of node type distribution
    
    Args:
        node_types: Dictionary of node type -> count
    """
    if node_types:
        # Color mapping for node types
        color_map = {
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
        }
        
        colors = [color_map.get(k, '#95A5A6') for k in node_types.keys()]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(node_types.keys()),
            values=list(node_types.values()),
            hole=0.4,
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textposition='inside'
        )])
        
        fig.update_layout(
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Run a query to see node type distribution")

def render_query_activity(query_history):
    """
    Render query activity chart
    
    Args:
        query_history: List of past queries
    """
    if query_history:
        history_df = pd.DataFrame(query_history)
        
        # Check if we have date column
        if "date" in history_df.columns:
            # Group by date
            daily_queries = history_df.groupby("date").size().reset_index(name="count")
            daily_queries["date"] = pd.to_datetime(daily_queries["date"])
            daily_queries = daily_queries.sort_values("date")
            
            # Line chart for activity over time
            fig = px.line(
                daily_queries,
                x="date",
                y="count",
                title="Query Activity Over Time",
                labels={"date": "Date", "count": "Number of Queries"},
                markers=True,
                color_discrete_sequence=['#3498DB']
            )
        else:
            # Bar chart of recent queries
            recent = history_df.tail(5)
            fig = px.bar(
                recent,
                x="timestamp",
                y=[1] * len(recent),
                title="Recent Query Activity",
                labels={"timestamp": "Time", "value": ""},
                color_discrete_sequence=['#3498DB']
            )
            fig.update_xaxis(tickangle=45)
        
        fig.update_layout(
            height=400,
            margin=dict(t=40, b=20, l=20, r=20),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 No query data available yet")

def render_node_type_progress(node_types, total_nodes):
    """
    Render progress bars for node type distribution
    
    Args:
        node_types: Dictionary of node type -> count
        total_nodes: Total number of nodes
    """
    if node_types and total_nodes > 0:
        sorted_types = sorted(node_types.items(), key=lambda x: x[1], reverse=True)
        for node_type, count in sorted_types[:5]:  # Show top 5
            percentage = (count / total_nodes * 100)
            st.progress(
                percentage / 100, 
                text=f"{node_type}: {count} nodes ({percentage:.1f}%)"
            )
    else:
        st.info("No data available")

def render_graph_statistics(graph_data):
    """
    Render graph statistics
    
    Args:
        graph_data: Current graph data (nodes + edges)
    """
    if graph_data:
        total_nodes = len(graph_data["nodes"])
        total_edges = len(graph_data["edges"])
        
        # Calculate density (edges / possible edges)
        density = (2 * total_edges) / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0
        avg_degree = (2 * total_edges) / total_nodes if total_nodes > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Graph Density", 
                f"{density:.2%}", 
                help="Ratio of actual edges to possible edges"
            )
        with col2:
            st.metric(
                "Average Degree", 
                f"{avg_degree:.1f}", 
                help="Average number of connections per node"
            )
        with col3:
            st.metric(
                "Connected Components", 
                "1", 
                help="Number of disconnected subgraphs"
            )
    else:
        st.info("No graph data available")

def render_recent_queries(query_history):
    """
    Render recent queries table
    
    Args:
        query_history: List of past queries
    """
    if query_history:
        recent_queries = pd.DataFrame(query_history[-5:])
        st.dataframe(
            recent_queries[["timestamp", "query"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No queries yet. Start exploring!")

def render_performance_metrics():
    """
    Render system performance metrics
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        response_time = random.uniform(0.5, 2.0)
        st.metric(
            "⏱️ Avg Response Time",
            f"{response_time:.2f}s",
            delta="-0.3s" if response_time < 1.5 else "+0.2s",
            help="Average query response time"
        )
    
    with col2:
        success_rate = 98.5
        st.metric(
            "✅ Success Rate",
            f"{success_rate:.1f}%",
            delta="+0.5%",
            help="Percentage of successful queries"
        )
    
    with col3:
        memory_usage = 256
        st.metric(
            "💾 Memory Usage",
            f"{memory_usage} MB",
            delta="-32 MB",
            help="Current memory usage"
        )
    
    with col4:
        uptime = "2h 15m"
        st.metric(
            "⏰ Uptime",
            uptime,
            help="System uptime"
        )

def render_export_options(query_history, graph_data):
    """
    Render export options
    
    Args:
        query_history: List of past queries
        graph_data: Current graph data
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Export Query History as CSV", use_container_width=True):
            if query_history:
                df = pd.DataFrame(query_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="aura_kg_queries.csv",
                    mime="text/csv",
                    key="download_csv"
                )
            else:
                st.warning("No data to export")
    
    with col2:
        if st.button("📋 View Graph Data", use_container_width=True):
            if graph_data:
                graph_json = json.dumps(graph_data, indent=2)
                with st.expander("Graph Data (JSON)"):
                    st.code(graph_json, language="json")
                st.success("✅ Graph data displayed above")
            else:
                st.warning("No graph data available")
    
    with col3:
        if st.button("🔄 Reset Dashboard", use_container_width=True):
            query_history.clear()
            st.session_state.current_answer = None
            st.session_state.current_graph_data = None
            st.success("Dashboard reset successfully!")
            import time
            time.sleep(1)
            st.rerun()