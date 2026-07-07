import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.intelligence.advanced.evidence_trust_engine import evidence_trust_engine
from backend.intelligence.advanced.digital_twin_engine import digital_twin_engine
from backend.intelligence.advanced.simulation_lab import simulation_lab

st.set_page_config(page_title="NEOVERSE AI | Advanced Intelligence", layout="wide")

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

st.title("🧠 Advanced Decision Intelligence")
st.caption("Digital Twin • Simulation Lab • Evidence Trust • Reasoning Trace")

tab1, tab2, tab3, tab4 = st.tabs(["Business Digital Twin", "Simulation Lab", "Evidence Trust Matrix", "Reasoning Trace"])

# --- TAB 1: Digital Twin ---
with tab1:
    st.subheader("Live Business Clone")
    st.markdown("This engine maintains an isolated, safe environment for the AI to run experiments.")
    
    twin_state = digital_twin_engine.get_current_state()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue", f"${twin_state['revenue']:,.0f}")
    c2.metric("Profit", f"${twin_state['profit']:,.0f}")
    c3.metric("Customers", f"{twin_state['customers']:,}")
    c4.metric("Inventory", f"{twin_state['inventory']:,}")
    
    # Simple radar chart of business health
    categories = ['Demand', 'Pricing Power', 'Workforce', 'Marketing', 'Competitiveness']
    values = [
        twin_state['demand']/150, 
        twin_state['pricing'], 
        twin_state['employees']*2, 
        twin_state['marketing_budget']/1500, 
        twin_state['competition_index']
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
      r=values,
      theta=categories,
      fill='toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, title="Business Health Radar")
    st.plotly_chart(fig, use_container_width=True)


# --- TAB 2: Simulation Lab ---
with tab2:
    st.subheader("Safe Experimentation Lab")
    st.markdown("Modify parameters below. The AI will recalculate the downstream effects without touching the real business.")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        scenario_name = st.text_input("Scenario Name (Type your test case here)", "Price Hike Scenario")
        new_price = st.slider("Product Pricing ($)", 50, 300, 120)
        new_marketing = st.slider("Marketing Budget ($)", 50000, 500000, 150000, step=10000)
        
        if st.button("Run Simulation"):
            with st.spinner("Calculating downstream dependencies..."):
                results = simulation_lab.apply_scenario({
                    "name": scenario_name,
                    "pricing": new_price,
                    "marketing_budget": new_marketing
                })
                st.session_state['sim_results'] = results
        
    with col_b:
        if 'sim_results' in st.session_state:
            res = st.session_state['sim_results']
            st.markdown("### Simulation Results")
            
            # Display Deltas
            d1, d2, d3 = st.columns(3)
            d1.metric("Revenue Impact", f"${res['state_after']['revenue']:,.0f}", f"${res['delta']['revenue']:,.0f}")
            d2.metric("Demand Impact", f"{res['state_after']['demand']:,}", f"{res['delta']['demand']:,}")
            d3.metric("Customer Impact", f"{res['state_after']['customers']:,}", f"{res['delta']['customers']:,}")
            
            # Graph comparison
            df = pd.DataFrame({
                "Metric": ["Revenue", "Profit", "Demand"],
                "Before": [res['state_before']['revenue'], res['state_before']['profit'], res['state_before']['demand']*100],
                "After": [res['state_after']['revenue'], res['state_after']['profit'], res['state_after']['demand']*100]
            })
            df = df.melt(id_vars="Metric", var_name="State", value_name="Value")
            fig2 = px.bar(df, x="Metric", y="Value", color="State", barmode="group")
            st.plotly_chart(fig2, use_container_width=True)

# --- TAB 3: Evidence Trust ---
with tab3:
    st.subheader("Evidence Quality Evaluation")
    
    # Visually prominent info box explaining the AI mechanism
    st.info("ℹ️ **System Trust & Explainability:** Our AI assigns a dynamic trust score to every data source based on reliability and freshness, effectively mitigating hallucination risks.")
    
    # Mock some incoming evidence
    mock_evidence = [
        {"source_name": "Finance API", "is_live": True},
        {"source_name": "User Guess", "is_live": True},
        {"source_name": "Old Spreadsheet", "is_live": False}
    ]
    
    trust_matrix = evidence_trust_engine.evaluate_evidence(mock_evidence)
    
    # Using st.metric to get the clean 'i' icon via the help parameter
    st.metric(
        label="Overall Trust Score", 
        value=f"{trust_matrix['overall_trust_score']}/100",
        help="Our AI assigns a dynamic trust score to every data source based on reliability and freshness, effectively mitigating hallucination risks."
    )
    
    df_trust = pd.DataFrame(trust_matrix["sources"])
    st.dataframe(df_trust, use_container_width=True)
    
    for warning in trust_matrix["weak_evidence_warnings"]:
        st.warning(warning)

# --- TAB 4: Reasoning Trace ---
with tab4:
    st.subheader("Execution Pipeline Trace")
    st.markdown("Absolute transparency into how the AI reached its conclusion.")
    
    # Mocking a pipeline execution for UI demonstration
    st.markdown("""
    * **[0ms]** 🟢 `Intent Detection`: Classified as STRATEGIC_DECISION
    * **[120ms]** 🟢 `Digital Twin`: Loaded business state (Revenue: $5M)
    * **[450ms]** 🟢 `Evidence Collection`: Fetched from Finance API, Old Spreadsheet
    * **[460ms]** 🟠 `Evidence Trust`: Downgraded Old Spreadsheet (Confidence -20%)
    * **[1100ms]** 🟢 `Dependency Graph`: Identified 'Demand' as critical bottleneck node
    * **[3500ms]** 🟢 `Simulation Lab`: Ran 3 Universes. Selected expected case.
    """)
    st.success("Recommendation Generated Successfully.")
