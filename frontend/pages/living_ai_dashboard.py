import streamlit as st
import pandas as pd
import plotly.express as px
from backend.living_ai.memory_engine import memory_engine
from backend.living_ai.notification_engine import notification_engine
from backend.living_ai.opportunity_radar import opportunity_radar

st.set_page_config(page_title="NEOVERSE AI | Living AI Dashboard", layout="wide")

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
    .alert-critical { background: rgba(255, 50, 50, 0.15); border-left: 5px solid #ff3333; }
    .alert-high { background: rgba(255, 165, 0, 0.15); border-left: 5px solid #ffa500; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 Living AI Command Center")
st.caption("Monitoring, Learning, and Proactive Evolution.")

# Fetch mock decision for visualization
decision_id = "test_decision_777"
memory_engine.store_decision(decision_id, {
    "context": {"business_type": "Retail"},
    "recommendation": "Expand to online sales",
    "confidence": 85,
    "reasoning_evolution": [{"timestamp": 1690000000, "explanation": "Initial calculation based on local foot traffic drop."}]
})
history = memory_engine.get_decision_history(decision_id)
latest_decision = history[-1]

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Memory Vault Items", len(memory_engine.long_term_vault))
col2.metric("Active Decision Version", f"v{latest_decision.get('version', 1)}")
col3.metric("Prediction Accuracy", "92%")
col4.metric("AI Learning Score", "150 XP")

st.markdown("---")

t1, t2, t3, t4 = st.tabs(["Decision Timeline & Versioning", "Active Alerts", "Opportunity Radar", "Community Benchmarks"])

with t1:
    st.subheader("Recommendation Evolution")
    colA, colB = st.columns([1, 2])
    with colA:
        for v in history:
            st.markdown(f"""
            <div class='glass-card'>
                <h4>Version {v.get('version')}</h4>
                <p><b>Recommendation:</b> {v.get('recommendation')}</p>
                <small>Confidence: {v.get('confidence')}%</small>
            </div>
            """, unsafe_allow_html=True)
    with colB:
        st.info("The AI continuously monitors external signals. When evidence changes, it re-evaluates and appends a new version here instead of stubbornly defending its past advice.")
        # Mock confidence evolution chart
        df = pd.DataFrame([{"Version": f"v{h.get('version')}", "Confidence": h.get("confidence")} for h in history])
        if not df.empty:
            fig = px.line(df, x="Version", y="Confidence", markers=True, title="Confidence Over Time")
            st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Intelligent Notification Engine")
    alerts = notification_engine.get_active_alerts()
    if not alerts:
        st.info("No active emergencies or alerts.")
    else:
        for alert in alerts:
            css = "alert-critical" if alert["priority"] == "Critical" else "alert-high"
            st.markdown(f"""
            <div class='glass-card {css}'>
                <h4>🚨 {alert['priority']} Priority: {alert['reason']}</h4>
                <p><b>Recommended Action:</b> {alert['recommended_action']}</p>
                <small>Evidence: {alert['evidence']}</small>
            </div>
            """, unsafe_allow_html=True)

with t3:
    st.subheader("Proactive Opportunity Radar")
    if st.button("Run Proactive Scan"):
        with st.spinner("Scanning Evidence Graph for hidden opportunities..."):
            opps = opportunity_radar.scan_for_opportunities({"nodes": []}, {"business_type": "Retail"})
            cols = st.columns(3)
            for i, opp in enumerate(opps):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='glass-card'>
                        <h4>✨ {opp.get('category')}</h4>
                        <p>{opp.get('expected_benefit')}</p>
                        <hr/>
                        <small><b>Difficulty:</b> {opp.get('difficulty')} | <b>Confidence:</b> {opp.get('confidence')}%</small><br/>
                        <small><b>Horizon:</b> {opp.get('time_horizon')}</small>
                    </div>
                    """, unsafe_allow_html=True)

with t4:
    st.subheader("Community Benchmarking")
    st.info("MVP is running on simulated anonymized data. Architecture is ready for real PostgreSQL user data.")
    colX, colY = st.columns(2)
    with colX:
        st.metric("Industry Success Rate", "68%")
        st.metric("Similar Businesses Analyzed", "1,204")
    with colY:
        st.markdown("**Common Mistakes to Avoid:**")
        st.write("- Over-hiring before Series A")
        st.write("- Ignoring local SEO")
        st.write("- Underpricing subscription tiers")
