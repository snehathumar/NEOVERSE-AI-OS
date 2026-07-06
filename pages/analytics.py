import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.analytics_service import analytics_service

st.set_page_config(page_title="NEOVERSE | Analytics", page_icon="📊", layout="wide")

def apply_custom_css():
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
    .bq-connected { color: #2563eb; font-weight: bold; }
    .alert-critical { background: #fef2f2; border-left: 5px solid #ef4444; }
    .alert-high { background: #fffbeb; border-left: 5px solid #f59e0b; }
    .badge { padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85em; display: inline-block; margin-bottom: 10px; }
    .badge-Pending { background: #fef3c7; color: #b45309; }
    .badge-Approved { background: #d1fae5; color: #047857; }
    .badge-Rejected { background: #fee2e2; color: #b91c1c; }
</style>
    """, unsafe_allow_html=True)

def render_dashboard():
    apply_custom_css()
    
    st.markdown('<h1>NEOVERSE <span style="font-weight:300; color:#94a3b8;">Analytics</span></h1>', unsafe_allow_html=True)
    
    # 1. GPU Analytics Layer
    st.markdown("### GPU Analytics Layer (cuDF / RAPIDS)")
    gpu_data = analytics_service.get_gpu_benchmark_results()
    
    gpu_col1, gpu_col2, gpu_col3 = st.columns(3)
    with gpu_col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="metric-value" style="color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8;">{gpu_data['pandas_cpu_time_seconds']}s</div>
            <p>Pandas (CPU)</p>
        </div>
        """, unsafe_allow_html=True)
    with gpu_col2:
        cudf_val = f"{gpu_data['cudf_gpu_time_seconds']}s" if gpu_data['gpu_available'] else "N/A"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; border-bottom: 3px solid #10b981;">
            <div class="metric-value">{cudf_val}</div>
            <p>cuDF (GPU)</p>
        </div>
        """, unsafe_allow_html=True)
    with gpu_col3:
        speedup_val = f"{gpu_data['speedup_factor']}x" if gpu_data['gpu_available'] else "N/A"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; border-bottom: 3px solid #3b82f6;">
            <div class="gpu-metric">{speedup_val}</div>
            <p>Speed Improvement</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")

    # 2. Key Metrics
    metrics = analytics_service.get_dashboard_metrics()
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f'<div class="glass-card" style="text-align:center;"><div class="metric-value">{metrics["avg_accuracy"]}%</div><p>AI Accuracy vs Reality</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="glass-card" style="text-align:center;"><div class="metric-value">{metrics["open_opportunities"]}</div><p>Detected Opportunities</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="glass-card" style="text-align:center;"><div class="metric-value">{metrics["overall_risk"]}</div><p>Aggregate Risk Exposure</p></div>', unsafe_allow_html=True)

    # 3. Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### Risk & Revenue Trends")
        st.area_chart(analytics_service.get_risk_revenue_trends(), height=300)
        
    with c2:
        st.markdown("### AI Confidence Trends")
        st.line_chart(analytics_service.get_confidence_trends(), height=300)

    st.markdown("### Opportunity Detection (Market Intelligence)")
    st.dataframe(analytics_service.get_opportunities(), use_container_width=True)
    
    st.markdown("### Prediction Accuracy Breakdown")
    st.bar_chart(analytics_service.get_accuracy_metrics(), height=250)

if __name__ == "__main__":
    render_dashboard()
