import streamlit as st
import pandas as pd
import plotly.express as px
from backend.living_layer.knowledge_manager import knowledge_manager
from backend.living_layer.memory_service import memory_service

st.set_page_config(page_title="NEOVERSE AI | Living Intelligence", layout="wide")

st.markdown("""
<style>
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        color: white;
    }
    .alert-critical {
        background: rgba(255, 50, 50, 0.15);
        border-left: 5px solid #ff3333;
    }
    .alert-high {
        background: rgba(255, 165, 0, 0.15);
        border-left: 5px solid #ffa500;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Living Intelligence Platform")

# Sidebar: Select Decision
st.sidebar.header("Decision Vault")
all_decisions = memory_service.get_all_decisions()
if not all_decisions:
    st.info("No decisions stored in memory yet. Run the Validation Pipeline first.")
    st.stop()

decision_options = {d["state_data"]["session_id"]: f"{d['state_data']['decision_type']} - {d['timestamp']}" for d in all_decisions}
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
with st.spinner("Loading Living Intelligence..."):
    dashboard = knowledge_manager.get_dashboard_data(selected_id)

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
            fig.update_layout(yaxis_range=[0,100], template="plotly_dark")
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
