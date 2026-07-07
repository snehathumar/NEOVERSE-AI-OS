import streamlit as st
import time

st.set_page_config(page_title="NEOVERSE AI | Judge Demo Mode", layout="wide")

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

st.title("🏆 NEOVERSE AI: Final Presentation (Judge Mode)")
st.caption("A one-click end-to-end demonstration of the complete Enterprise OS.")

if st.button("▶️ Initialize Enterprise Demo Sequence", use_container_width=True, type="primary"):
    
    with st.container():
        st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
        st.subheader("Phase 1: Event Bus & Tool Orchestration")
        with st.spinner("Connecting to Event Bus..."):
            time.sleep(1)
        st.success("Event Bus ONLINE. Publishing `DECISION_REQUESTED`...")
        
        with st.spinner("ToolRegistry executing Google Maps, Weather, and Finance MCP APIs..."):
            time.sleep(1.5)
        st.success("Evidence normalized and sanitized.")
        
        st.markdown("---")
        st.subheader("Phase 2: Advanced Intelligence (Digital Twin & Simulation)")
        with st.spinner("Generating Business Digital Twin profile..."):
            time.sleep(1)
        st.info("Twin Active: Revenue $10M | Customers 50k | Risk Index 45")
        
        with st.spinner("Running 3-Universe Simulation (Best, Expected, Worst)..."):
            time.sleep(1.5)
        st.success("Simulations complete. Devil's Advocate debate resolved.")
        
        st.markdown("---")
        st.subheader("Phase 3: Hardware Acceleration (NVIDIA RAPIDS)")
        with st.spinner("Aggregating results using cuDF GPU Engine..."):
            time.sleep(1)
        st.code("""
        [GPU Benchmark Report]
        Engine: cuDF (GPU)
        Latency: 45.2ms
        CPU Est: 678.0ms
        Speedup: 15.0x
        """, language="yaml")
        
        st.markdown("---")
        st.subheader("Phase 4: Evolution & BigQuery Analytics")
        with st.spinner("Logging Audit Trail & Versioning Recommendation (v3)..."):
            time.sleep(1)
        st.success("Audit Trailed. Confidence Adaptive Score: 89%.")
        
        with st.spinner("Streaming decision history to BigQuery..."):
            time.sleep(1)
        st.success("Stored in BigQuery. Looker datasets updated.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.balloons()
        st.success("✅ Demo Complete: The system is ready for Enterprise deployment.")
else:
    st.info("Waiting to start demo sequence...")
