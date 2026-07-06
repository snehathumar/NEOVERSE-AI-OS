import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.decision_engine import decision_engine

st.set_page_config(page_title="NEOVERSE AI | Executive Validation", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    body, .stApp { font-family: 'Roboto', sans-serif; background-color: #f8f9fa; color: #202124; }
    .glass-card { background: #ffffff; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15); border: 1px solid #dadce0; color: #202124; }
    .minority-card { background: #fce8e6; border: 1px solid #fad2cf; color: #a50e0e; }
    .expert-avatar { font-size: 2rem; margin-right: 10px; }
    h1, h2, h3 { color: #202124 !important; font-weight: 500; }
    hr { border-top: 1px solid #dadce0; }
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
            fig_conf.update_layout(yaxis_range=[0,100], template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
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
            fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, title="Structured Uncertainty Matrix", template="plotly_white", margin=dict(t=40, b=0, l=0, r=0))
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
            # Extracted visual representation
            agent_role = v.get("agent", "Agent")
            vote_val = v.get("vote", "N/A")
            justification = v.get("justification", "")
            
            # Use color based on vote
            vote_color = "#10b981" if "APPROVE" in str(vote_val).upper() else "#ef4444"
            if "CONDITIONAL" in str(vote_val).upper(): vote_color = "#f59e0b"
            
            st.markdown(f'''
            <div class="glass-card">
                <div style="display:flex; align-items:center; margin-bottom:10px;">
                    <span class="expert-avatar">🧑‍💼</span>
                    <div>
                        <b style="font-size:1.1rem;">{agent_role}</b><br/>
                        <span style="color: {vote_color}; font-weight:600; font-size:0.9rem;">VOTE: {vote_val}</span>
                    </div>
                </div>
                <hr style="margin: 10px 0;"/>
                <p style="font-size:0.9rem; color:#5f6368; font-weight:500; margin-bottom:4px;">REASONING:</p>
                <small style="color:#3c4043; line-height:1.4;">{justification}</small>
            </div>
            ''', unsafe_allow_html=True)
            
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
else:
    st.info("👈 Please enter the Decision Context in the sidebar and click **Initialize Validation Pipeline** to begin.")
    
    st.markdown("""
    ### Welcome to the Enterprise Decision Validation Layer
    This powerful module orchestrates a 13-stage AI pipeline to rigorously test, debate, and validate any strategic business decision before execution. 
    
    **Pipeline Stages Include:**
    - **Multi-Agent Debate Floor:** Specialized AI agents (CFO, CTO, Risk Officer) argue for and against the decision.
    - **Devil's Advocate Engine:** Actively tries to destroy the underlying assumptions.
    - **Self-Doubt Engine:** Identifies what the AI *doesn't* know.
    - **Reality Check & 6-Pillar Risk Assessment:** Ensures the decision is practical and measures risk across 6 critical business dimensions.
    
    *Awaiting Input...*
    """)
