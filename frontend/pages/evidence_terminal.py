import streamlit as st
import pandas as pd
from backend.monitoring.api_monitor import api_monitor
from backend.monitoring.model_monitor import model_monitor
from backend.cache.cache_manager import cache_manager
from backend.tool_registry.tool_manager import tool_manager
from backend.tool_registry.tool_base import tool_registry
from backend.evidence.evidence_store import evidence_store
import backend.tool_registry.tools.sample_tools

st.set_page_config(page_title="NEOVERSE AI | Evidence Terminal", layout="wide")

st.markdown("""
<style>
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        color: white;
    }
    .status-healthy { color: #00ff00; font-weight: bold; }
    .status-cooldown { color: #ff9900; font-weight: bold; }
    .status-degraded { color: #ff3333; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🛰️ Live Intelligence Command Center")
st.caption("Evidence Graph, API Health, Cache Status, and Dynamic Model Routing.")

session_id = "test_session_001"
graph = evidence_store.get_or_create_graph(session_id)

col1, col2, col3, col4 = st.columns(4)
cache_stats = cache_manager.get_stats()
col1.metric("Cache Hits", cache_stats["hits"])
col2.metric("Cache Misses", cache_stats["misses"])
col3.metric("Cache Hit Ratio", f"{cache_stats['hit_ratio_percent']}%")
col4.metric("Active Model", model_monitor.get_stats().get("active_model", "None"))

st.markdown("---")

colA, colB, colC = st.columns([1.5, 1, 1])

with colA:
    st.subheader("Simulate Capability Request")
    st.info("Gemini asks for 'capabilities', not raw API endpoints.")
    
    available_caps = list(tool_registry.get_all_tools().keys())
    cap_choice = st.selectbox("Request Capability", available_caps)
    param_input = st.text_input("Parameter (e.g., 'New York' or 'AAPL')", "New York")
    
    if st.button("Execute Request"):
        with st.spinner(f"Routing to {cap_choice} Tool..."):
            param_key = "location" if cap_choice in ["Weather", "Traffic"] else ("symbol" if cap_choice == "Finance" else "query")
            
            # Execute through ToolManager
            structured_evidence = tool_manager.execute_capability(cap_choice, {param_key: param_input}, category="Live Simulation")
            
            # Ingest to Evidence Graph
            graph.ingest_structured_evidence(structured_evidence)
            
            st.success("Evidence Ingested and Normalized!")
            with st.expander("View Structured Evidence"):
                st.json(structured_evidence)

with colB:
    st.subheader("API Health & Routing")
    api_stats = api_monitor.get_stats()
    
    if not api_stats:
        st.info("No API traffic yet.")
    
    for api_name, stats in api_stats.items():
        s_class = "status-healthy" if stats["status"] == "Online" else "status-degraded"
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🌐 {api_name} API</h4>
            <p>Status: <span class='{s_class}'>{stats['status']}</span></p>
            <small>Latency: {stats['average_response_time_ms']:.1f}ms</small><br/>
            <small>Success: {stats['success_count']} | Fails: {stats['failure_count']}</small>
        </div>
        """, unsafe_allow_html=True)

with colC:
    st.subheader("Model Health & Cooldowns")
    model_stats = model_monitor.get_stats()["metrics"]
    
    if not model_stats:
        st.info("No LLM invocations yet.")
        
    for model_name, stats in model_stats.items():
        s_class = "status-healthy" if stats["status"] == "Ready" else "status-cooldown"
        st.markdown(f"""
        <div class='glass-card'>
            <h4>🧠 {model_name}</h4>
            <p>Status: <span class='{s_class}'>{stats['status']}</span></p>
            <small>Health Score: {stats['health_score']}/100</small><br/>
            <small>Fails: {stats['failure_count']}</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Central Evidence Graph")
st.caption("This graph is consumed by the Decision Engine, Parallel Universe, and Monitoring AI.")

graph_data = graph.get_graph()
if graph_data["nodes"]:
    st.json(graph_data)
else:
    st.info("Evidence Graph is empty. Request a capability to populate it.")
