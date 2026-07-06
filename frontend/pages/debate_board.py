import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.decision_engine import decision_engine

st.set_page_config(page_title="NEOVERSE AI | Executive Validation", layout="wide")

st.markdown("""
<style>
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        color: white;
    }
    .minority-card {
        background: rgba(255, 50, 50, 0.1);
        border: 1px solid rgba(255, 50, 50, 0.3);
    }
    .expert-avatar {
        font-size: 2rem;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Enterprise Decision Validation Layer")

with st.sidebar:
    st.header("Decision Input")
    domain = st.selectbox("Decision Domain", ["Pricing", "Hiring", "Expansion", "Marketing", "Investment", "Operations", "Emergency"])
    decision_context = st.text_area("Decision Context", "Should we increase our core product pricing by 20% to offset rising supply chain costs?")
    run_btn = st.button("Initialize Validation Pipeline", type="primary")

if run_btn:
    with st.spinner("Executing 13-Stage Enterprise Validation Pipeline..."):
        # We pass a simple mock business state
        business_state = {"annual_revenue": 1000000, "employees": 50, "risk_tolerance": "medium"}
        
        # Run pipeline
        res = decision_engine.run_full_simulation(decision_context, domain, business_state)
    
    if res.get("halt_pipeline"):
        st.error(f"🛑 Pipeline Halted: {res.get('halt_reason')}")
        st.warning(res.get("halt_interview_question"))
        st.stop()
        
    st.success("Validation Complete.")
    results = res.get("results", {})
    
    # 1. Top Level Metrics
    col1, col2, col3, col4 = st.columns(4)
    consensus = results.get("consensus_data", {})
    col1.metric("Agreement Score", f"{consensus.get('agreement_score', 0)}%")
    col2.metric("Conflict Level", f"{consensus.get('conflict_score', 0)}%")
    
    # Confidence Evolution
    conf_timeline = res.get("confidence_timeline", [])
    final_conf = conf_timeline[-1]["score"] if conf_timeline else 0
    col3.metric("Final Confidence", f"{final_conf}%")
    
    # Practicality
    reality = results.get("reality_check_data", {})
    is_prac = "✅ Practical" if reality.get("is_practical") else "❌ Impractical"
    col4.metric("Reality Check", is_prac)

    # 2. Confidence & Uncertainty Charts
    st.markdown("### 📊 Analytics & Confidence Evolution")
    c1, c2 = st.columns(2)
    
    with c1:
        if conf_timeline:
            df_conf = pd.DataFrame(conf_timeline)
            fig_conf = px.line(df_conf, x="stage", y="score", title="Confidence Evolution Timeline", markers=True)
            fig_conf.update_layout(yaxis_range=[0,100], template="plotly_dark")
            st.plotly_chart(fig_conf, use_container_width=True)
            
    with c2:
        uncert = res.get("uncertainty_matrix", {})
        if uncert:
            labels = ["Data", "Market", "Human Behavior", "External Event", "Model"]
            values = [
                uncert.get("data_uncertainty", 0),
                uncert.get("market_uncertainty", 0),
                uncert.get("human_behavior_uncertainty", 0),
                uncert.get("external_event_uncertainty", 0),
                uncert.get("model_uncertainty", 0)
            ]
            fig_rad = go.Figure(data=go.Scatterpolar(
                r=values + [values[0]],
                theta=labels + [labels[0]],
                fill='toself'
            ))
            fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, title="Structured Uncertainty Matrix", template="plotly_dark")
            st.plotly_chart(fig_rad, use_container_width=True)

    # 3. The Debate Floor
    st.markdown("### 🏛️ The Debate Floor")
    votes = results.get("round_3_votes", [])
    
    # Highlight Minority Report if exists
    if consensus.get("minority_report"):
        st.markdown(f'<div class="glass-card minority-card">🚨 <b>Minority Report Triggered</b><br/>{consensus.get("minority_report")}</div>', unsafe_allow_html=True)
        
    cols = st.columns(len(votes) if votes else 1)
    for idx, v in enumerate(votes):
        with cols[idx]:
            st.markdown(f'<div class="glass-card"><span class="expert-avatar">🧑‍💼</span><b>{v.get("agent")}</b><br/>Vote: {v.get("vote")}<hr/><small>{v.get("justification")}</small></div>', unsafe_allow_html=True)
            
    # 4. Intelligence Panels
    st.markdown("### 🧠 Post-Debate Intelligence")
    
    t1, t2, t3, t4 = st.tabs(["Devil's Advocate", "Self Doubt Engine", "6-Pillar Risk", "Alternative Strategies"])
    
    with t1:
        da = results.get("devils_advocate_data", {})
        st.markdown(f"**Opposition Argument:** {da.get('opposition_argument')}")
        st.markdown("**Hidden Risks Exposed:**")
        for hr in da.get("hidden_risks_exposed", []):
            st.write(f"- {hr}")
            
    with t2:
        sd = results.get("self_doubt_data", {})
        st.write("**Vulnerable Assumptions:**")
        st.write(sd.get("vulnerable_assumptions", []))
        st.write("**Missing Information:**")
        st.write(sd.get("missing_information", []))
        
    with t3:
        risk = results.get("risk_assessment_data", {})
        st.json(risk)
        
    with t4:
        alts = results.get("alternative_strategies_data", {})
        for k, v in alts.items():
            st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

    # 5. Reasoning Trace (System Logs)
    with st.expander("🔍 View Decision Reasoning Trace"):
        trace = res.get("decision_trace", [])
        for log in trace:
            st.text(log)
