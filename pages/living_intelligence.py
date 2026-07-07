import streamlit as st
import pandas as pd
import plotly.express as px
from backend.living_layer.knowledge_manager import knowledge_manager
from backend.repositories.decision_repo import DecisionRepository
import importlib
import sys

# Force reload backend modules to clear Streamlit cache of old bytecode
if "backend.llm_client" in sys.modules:
    importlib.reload(sys.modules["backend.llm_client"])
if "backend.living_layer.opportunity_engine" in sys.modules:
    importlib.reload(sys.modules["backend.living_layer.opportunity_engine"])
if "backend.living_layer.knowledge_manager" in sys.modules:
    importlib.reload(sys.modules["backend.living_layer.knowledge_manager"])
    from backend.living_layer.knowledge_manager import knowledge_manager


st.set_page_config(page_title="NEOVERSE AI | Living Intelligence", layout="wide")

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

st.title("🌱 Living Intelligence Platform")

# Sidebar: Select Decision
st.sidebar.header("Decision Vault")
try:
    all_decisions = DecisionRepository().query()
except Exception as e:
    all_decisions = []
    
if not all_decisions:
    st.info("No decisions stored in memory yet. Run the Validation Pipeline first.")
    st.stop()

decision_options = {d.get("id") or d.get("session_id", f"ID-{i}"): f"Decision - {d.get('prompt', 'Unknown')[:30]}... ({d.get('created_at', d.get('timestamp', ''))[:10]})" for i, d in enumerate(all_decisions)}
selected_id = st.sidebar.selectbox("Select Tracked Decision", options=list(decision_options.keys()), format_func=lambda x: decision_options[x])

# Top Right: Simulate Live Signal
st.sidebar.markdown("---")
st.sidebar.subheader("Simulate Market Signal")
signal_type = st.sidebar.selectbox("Signal Event", ["Competitor dropped prices by 30%", "Major supply chain disruption", "Revenue crashed by 40%"])
if st.sidebar.button("Send Signal"):
    with st.spinner("Processing Signal..."):
        res = knowledge_manager.process_live_signal(selected_id, {"headline": signal_type})
        if res.get("status") == "Decision Updated":
            st.sidebar.success("Signal Processed: AI updated its recommendation!")
        else:
            st.sidebar.warning(res.get("status"))

# Load Dashboard Data
@st.cache_data(ttl=300, show_spinner=False)
def load_dashboard_data(decision_id):
    return knowledge_manager.get_dashboard_data(decision_id)

with st.spinner("🧠 Booting up 3 concurrent AI Engines (Opportunity, Future, Community). This can take up to 15 seconds..."):
    dashboard = load_dashboard_data(selected_id)

if not dashboard:
    st.error("Failed to load dashboard data.")
    st.stop()

state_data = dashboard["latest_state"]
history = dashboard["history"]
latest_version = history[-1]["version"]

st.markdown(f"### Context: {state_data.get('decision_context')}")
st.caption(f"Currently tracking Version {latest_version} • Decision ID: {selected_id}")

t1, t2, t3, t4, t5 = st.tabs([
    "Decision Timeline", 
    "Alert & Emergency Center", 
    "Opportunity Radar", 
    "Future & Community", 
    "Decision Vault (Raw)"
])

with t1:
    st.subheader("Visual History & Confidence Evolution")
    timeline = dashboard["timeline"]
    df_timeline = pd.DataFrame(timeline)
    
    colA, colB = st.columns([1, 2])
    with colA:
        for item in timeline:
            st.markdown(f"""
            <div class='glass-card'>
                <small>{item['timestamp']}</small><br/>
                <b>v{item['version']} - {item['event']}</b><br/>
                {item['details']}
            </div>
            """, unsafe_allow_html=True)
            
    with colB:
        # Plot Confidence Evolution across versions
        conf_data = []
        for v in history:
            ver = v["version"]
            # Get the last confidence score of that version's timeline
            c_timeline = v["state_data"].get("confidence_timeline", [])
            if c_timeline:
                conf_data.append({"Version": f"v{ver}", "Confidence": c_timeline[-1]["score"]})
        
        if conf_data:
            df_conf = pd.DataFrame(conf_data)
            fig = px.line(df_conf, x="Version", y="Confidence", markers=True, title="Confidence Over Time")
            fig.update_layout(yaxis_range=[0,100], template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Active Alerts & Emergencies")
    alerts = state_data.get("results", {}).get("alerts", [])
    if not alerts:
        st.info("No active alerts.")
    
    for alert in alerts:
        css_class = "alert-critical" if alert.get("priority") == "Critical" else ("alert-high" if alert.get("priority") == "High" else "glass-card")
        st.markdown(f"""
        <div class='glass-card {css_class}'>
            <h3>🚨 {alert.get('priority')} Priority Alert</h3>
            <p><b>Reason:</b> {alert.get('reason')}</p>
            <p><b>Action:</b> {alert.get('suggested_action')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    em_plan = state_data.get("results", {}).get("emergency_plan")
    if em_plan:
        st.error("EMERGENCY MODE ACTIVATED")
        st.markdown(f"**Recovery Summary:** {em_plan.get('recovery_plan_summary')}")
        st.markdown("**Priority Actions:**")
        for a in em_plan.get("priority_actions", []):
            st.write(f"- {a}")

with t3:
    st.subheader("Proactive Opportunity Radar")
    opps = dashboard["opportunities"]
    cols = st.columns(3)
    for i, opp in enumerate(opps):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='glass-card'>
                <h4>✨ {opp.get('title')}</h4>
                <p>{opp.get('description')}</p>
                <hr/>
                <small><b>Impact:</b> {opp.get('expected_revenue_impact')}</small><br/>
                <small><b>Risk:</b> {opp.get('risk')} | <b>Effort:</b> {opp.get('effort')}</small>
            </div>
            """, unsafe_allow_html=True)

with t4:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Future Simulations (1-Year)")
        scenarios = dashboard["future_scenarios"]
        for s in scenarios:
            st.markdown(f"**{s.get('timeframe')}**: {s.get('headline')}<br/><small>{s.get('short_summary')}</small>", unsafe_allow_html=True)
            
    with col2:
        st.subheader("Community Benchmarking")
        comm = dashboard["community_insights"]
        st.metric("Similar Businesses Analyzed", comm.get("similar_businesses_analyzed", 0))
        st.markdown("**Most Successful Strategies:**")
        for s in comm.get("most_successful_strategies", []):
            st.write(f"- {s}")

with t5:
    st.subheader("Raw Decision Vault")
    selected_ver = st.selectbox("View Version", [h["version"] for h in history])
    ver_data = next(h for h in history if h["version"] == selected_ver)
    st.json(ver_data)
