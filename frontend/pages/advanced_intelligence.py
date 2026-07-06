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
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        color: white;
    }
    .trust-high { color: #00ff00; font-weight: bold; }
    .trust-low { color: #ff3333; font-weight: bold; }
    .delta-pos { color: #00ff00; }
    .delta-neg { color: #ff3333; }
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
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        new_price = st.slider("Product Pricing ($)", 50, 300, 120)
        new_marketing = st.slider("Marketing Budget ($)", 50000, 500000, 150000, step=10000)
        
        if st.button("Run Simulation"):
            with st.spinner("Calculating downstream dependencies..."):
                results = simulation_lab.apply_scenario({
                    "pricing": new_price,
                    "marketing_budget": new_marketing
                })
                st.session_state['sim_results'] = results
        st.markdown("</div>", unsafe_allow_html=True)
        
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
    st.markdown("Not all evidence is equal. The AI mathematically weighs sources based on reliability and freshness.")
    
    # Mock some incoming evidence
    mock_evidence = [
        {"source_name": "Finance API", "is_live": True},
        {"source_name": "User Guess", "is_live": True},
        {"source_name": "Old Spreadsheet", "is_live": False}
    ]
    
    trust_matrix = evidence_trust_engine.evaluate_evidence(mock_evidence)
    
    st.markdown(f"**Overall Trust Score: {trust_matrix['overall_trust_score']}/100**")
    
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
