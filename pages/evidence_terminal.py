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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    body, .stApp { font-family: 'Outfit', sans-serif; background-color: transparent; color: #1e293b; }
    .glass-card, .kpi-card, .metric-card { background: #ffffff; border-radius: 12px; padding: 24px; margin-bottom: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); transition: transform 0.2s, box-shadow 0.2s; color: #1e293b; }
    .glass-card:hover, .kpi-card:hover, .metric-card:hover { transform: translateY(-2px); border: 1px solid #cbd5e1; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }
    .minority-card { background: #fef2f2; border: 1px solid #fecaca; color: #ef4444; }
    .expert-avatar { font-size: 2rem; margin-right: 10px; }
    h1, h2, h3, h4, h5 { color: #0f172a !important; font-weight: 600; }
    hr { border-top: 1px solid #e2e8f0; }
    /* specific overrides */
    .status-ok { color: #10b981; font-weight: bold; }
    .status-warn { color: #f59e0b; font-weight: bold; }
    .status-alert { color: #ef4444; font-weight: bold; }
    .gpu-active { color: #10b981; font-weight: bold; }
    .gpu-inactive { color: #f59e0b; font-weight: bold; }
    .bq-connected { color: #4f46e5; font-weight: bold; }
    .alert-critical { background: #fef2f2; border-left: 5px solid #ef4444; }
    .alert-high { background: #fffbeb; border-left: 5px solid #f59e0b; }
    .badge { padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85em; display: inline-block; margin-bottom: 10px; }
    .badge-Pending { background: #fef3c7; color: #b45309; }
    .badge-Approved { background: #d1fae5; color: #047857; }
    .badge-Rejected { background: #fee2e2; color: #b91c1c; }
</style>
""", unsafe_allow_html=True)

st.title("🛰️ Live Intelligence Command Center")
st.caption("Evidence Graph, API Health, Cache Status, and Dynamic Model Routing.")

session_id = "test_session_001"
if "graph_reset" not in st.session_state:
    import importlib
    import backend.evidence.evidence_graph
    import backend.evidence.evidence_store
    importlib.reload(backend.evidence.evidence_graph)
    importlib.reload(backend.evidence.evidence_store)
    # Get the reloaded store
    evidence_store = backend.evidence.evidence_store.evidence_store
    evidence_store._active_graphs.clear()
    st.session_state.graph_reset = True
else:
    import backend.evidence.evidence_store
    evidence_store = backend.evidence.evidence_store.evidence_store

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
            
            with st.spinner("Generating Live AI Briefing..."):
                from backend.llm_client import orchestrator
                prompt = (
                    f"You are the NEOVERSE AI Command Center. You just ingested {cap_choice} data for '{param_input}'. "
                    f"The data is: {structured_evidence}. "
                    "In exactly 1-2 punchy sentences, give the user a strategic intelligence briefing on what this means or what's happening. "
                    "Do not use markdown blocks, just return the raw text."
                )
                ai_briefing = orchestrator.generate_text(prompt)
                
            st.info(f"🤖 **Command Center AI:** {ai_briefing}")
            
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

st.subheader("Central Evidence Graph")
st.caption("This graph is consumed by the Decision Engine, Parallel Universe, and Monitoring AI.")

from streamlit_agraph import agraph, Node, Edge, Config

graph_data = graph.get_graph()
if graph_data["nodes"]:
    nodes = []
    edges = []
    
    for node in graph_data["nodes"]:
        node_id = node.get("id", "unknown")
        node_type = node.get("type", "Node")
        data = node.get("data", {})
        
        if node_type == "ExternalEvidence":
            source = data.get("source", "Unknown")
            struct_data = data.get("structured_data", {})
            # Make label short and punchy
            primary_key = list(struct_data.keys())[0] if struct_data else "Data"
            primary_val = struct_data.get(primary_key, "Inbound")
            label_text = f"Live: {source}\n{primary_key}: {primary_val}"
            
            # Put the full payload in the title (tooltip)
            tooltip = f"Source: {source}\n" + "\n".join([f"{k}: {v}" for k, v in struct_data.items()])
            robot_url = f"https://api.dicebear.com/9.x/bottts/svg?seed={node_id}&backgroundColor=transparent"
            nodes.append(Node(id=node_id, label=label_text, title=tooltip, shape="image", image=robot_url, size=35, font={'color': 'white'}))
        elif node_type == "Core":
            name = data.get("name", node_id)
            robot_url = f"https://api.dicebear.com/9.x/bottts/svg?seed={name}&backgroundColor=transparent"
            nodes.append(Node(id=node_id, label=name, title=f"Core Intelligence Module: {name}", shape="image", image=robot_url, size=45, font={'color': 'white', 'size': 18}))
        else:
            robot_url = f"https://api.dicebear.com/9.x/bottts/svg?seed={node_id}&backgroundColor=transparent"
            nodes.append(Node(id=node_id, label=f"{node_type}\n{node_id}", shape="image", image=robot_url, size=25, font={'color': 'white'}))
            
    for edge in graph_data.get("edges", []):
        edges.append(Edge(source=edge.get("source"), target=edge.get("target"), label=edge.get("relation", ""), color="#718096"))
        
    config = Config(width="100%", height=600, directed=True, physics=True, hierarchical=False,
                    interaction={'zoomView': False, 'dragView': False}, # Disable zoom and pan
                    nodeHighlightBehavior=True, highlightColor="#F7A7A6",
                    node={'labelProperty':'label'}, link={'labelProperty': 'label', 'renderLabel': True})
    
    agraph(nodes=nodes, edges=edges, config=config)
    
    with st.expander("View Raw JSON Data"):
        st.json(graph_data)
else:
    st.info("Evidence Graph is empty. Request a capability to populate it.")
