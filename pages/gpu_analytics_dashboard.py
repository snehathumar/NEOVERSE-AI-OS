import streamlit as st
import pandas as pd
import plotly.express as px
from backend.analytics_core.benchmark.benchmark_engine import benchmark_engine
from backend.analytics_core.benchmark.explainability import explainability
from backend.analytics_core.gpu.gpu_engine import gpu_engine
from backend.analytics_core.bigquery.bq_client import bq_client

st.set_page_config(page_title="NEOVERSE AI | GPU Analytics", layout="wide")

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
    .gpu-active { color: #00ff00; font-weight: bold; }
    .gpu-inactive { color: #ff9900; font-weight: bold; }
    .bq-connected { color: #4285F4; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Enterprise Analytics & GPU Benchmarking")
st.caption("Central BigQuery Warehouse + NVIDIA RAPIDS Acceleration.")

col1, col2, col3 = st.columns(3)
with col1:
    s_class = "gpu-active" if gpu_engine.gpu_enabled else "gpu-inactive"
    s_text = "NVIDIA cuDF Active" if gpu_engine.gpu_enabled else "CPU (pandas) Fallback"
    st.markdown(f"<div class='glass-card'><h4>Hardware Layer</h4><p class='{s_class}'>{s_text}</p></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='glass-card'><h4>Analytics Core</h4><p class='bq-connected'>Google BigQuery</p></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='glass-card'><h4>Rows Processed</h4><p style='font-size: 20px; font-weight: bold;'>100,000+</p></div>", unsafe_allow_html=True)

st.markdown("---")

t1, t2 = st.tabs(["GPU Benchmark Engine", "Explainable Acceleration"])

with t1:
    st.subheader("Run Automated Performance Benchmark")
    rows_to_process = st.slider("Select Dataset Size (Rows)", min_value=10000, max_value=1000000, step=10000, value=100000)
    
    if st.button("Run Benchmark (pandas vs cuDF)"):
        with st.spinner("Executing mass aggregations..."):
            results = benchmark_engine.run_benchmark(num_rows=rows_to_process)
            
            # Save to mock BigQuery
            bq_client.insert_rows("benchmark_results", [results])
            
            # Display Results
            c1, c2, c3 = st.columns(3)
            c1.metric("CPU Time (pandas)", f"{results['cpu_execution_time_ms']} ms")
            c2.metric("GPU Time (cuDF)", f"{results['gpu_execution_time_ms']} ms")
            c3.metric("Speedup", results['speed_improvement'])
            
            # Graph
            df = pd.DataFrame([
                {"Environment": "CPU (pandas)", "Time (ms)": results['cpu_execution_time_ms']},
                {"Environment": "GPU (cuDF)", "Time (ms)": results['gpu_execution_time_ms']}
            ])
            fig = px.bar(df, x="Environment", y="Time (ms)", color="Environment", title="Execution Time Comparison (Lower is Better)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Store in session state for explainability tab
            st.session_state['latest_benchmark'] = results

with t2:
    st.subheader("Business Impact of Hardware Acceleration")
    if 'latest_benchmark' in st.session_state:
        explanation = explainability.explain_business_impact(st.session_state['latest_benchmark'])
        st.markdown(f"<div class='glass-card'>{explanation}</div>", unsafe_allow_html=True)
    else:
        st.info("Run a benchmark in the first tab to see explainability.")
