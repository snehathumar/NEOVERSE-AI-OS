import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.analytics_service import analytics_service

st.set_page_config(page_title="NEOVERSE | Analytics", page_icon="📊", layout="wide")

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    .stApp { 
        background: linear-gradient(135deg, #09090b 0%, #111827 100%);
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif; 
    }
    
    h1, h2, h3, h4, h5 { 
        color: #ffffff !important; 
        font-weight: 800; 
        letter-spacing: -0.5px; 
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value { 
        font-size: 2.5rem; 
        font-weight: 800; 
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .gpu-metric {
        font-size: 3rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
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
