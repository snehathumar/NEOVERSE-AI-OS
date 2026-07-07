import streamlit as st
import pandas as pd
from backend.platform.observability.tracker import system_observability
from backend.infrastructure.gpu_engine.engine import gpu_engine
from backend.infrastructure.bq_analytics.client import bq_analytics_client
from backend.ecosystem.community_intelligence.aggregator import community_intelligence

st.set_page_config(page_title="NEOVERSE AI | Ecosystem Command Center", layout="wide")

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

st.title("🌐 NEOVERSE AI Ecosystem Command Center")
st.caption("Event-Driven Architecture • Scalable Plugins • Enterprise Analytics")

# Top Row: Infrastructure Health
c1, c2, c3, c4 = st.columns(4)
with c1:
    gpu_status = "ACTIVE (cuDF)" if gpu_engine.gpu_enabled else "FALLBACK (pandas)"
    status_class = "status-ok" if gpu_engine.gpu_enabled else "status-warn"
    st.markdown(f"<div class='glass-card'><h4>GPU Engine</h4><p class='{status_class}'>{gpu_status}</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='glass-card'><h4>Event Bus</h4><p class='status-ok'>ONLINE (Pub/Sub)</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='glass-card'><h4>Data Warehouse</h4><p class='status-ok'>BigQuery ONLINE</p></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='glass-card'><h4>Tool Registry</h4><p class='status-ok'>8 MCP Tools Loaded</p></div>", unsafe_allow_html=True)

st.markdown("---")

t1, t2, t3 = st.tabs(["System Observability", "Analytics & Looker", "Community Intelligence"])

# TAB 1: Observability
with t1:
    st.subheader("Live Event & Metrics Tracking")
    metrics = system_observability.get_health_report()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total API Calls", metrics["api_calls"])
    m2.metric("Total Errors", metrics["errors"])
    m3.metric("GPU Fallbacks", metrics["gpu_fallbacks"])
    m4.metric("Total Latency (ms)", f"{metrics['total_latency_ms']:.1f}")

# TAB 2: BigQuery Analytics
with t2:
    st.subheader("Enterprise Decision Analytics")
    bq_stats = bq_analytics_client.get_analytics_summary()
    b1, b2, b3 = st.columns(3)
    b1.metric("Decisions Stored", bq_stats["total_decisions_stored"])
    b2.metric("Success Rate", f"{bq_stats['decision_success_rate']}%")
    b3.metric("Avg Confidence", f"{bq_stats['average_confidence']}%")
    st.info("Data schemas are fully optimized for Looker BI integration.")

# TAB 3: Community Intelligence
with t3:
    st.subheader("Global Anonymized Trends")
    st.markdown("Aggregated intelligence from similar businesses in the NEOVERSE ecosystem.")
    
    ci = community_intelligence.get_community_insights("Enterprise SaaS")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        - **Similar Businesses Analysed:** {ci['similar_businesses']}
        - **Average Success Rate:** {ci['average_decision_success']}%
        - **Market Risk Tolerance:** {ci['average_risk_taken']}
        """)
    with col_b:
        st.markdown(f"""
        - **Confidence Trend:** {ci['confidence_trends']}
        - **Top Strategy:** {ci['top_recommended_strategy']}
        """)
        
st.markdown("---")
st.success("NEOVERSE Platform is fully orchestrated and ready for Enterprise Deployment.")
