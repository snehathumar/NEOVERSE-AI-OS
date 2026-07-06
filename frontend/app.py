import streamlit as st
import pandas as pd
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.business_state import BusinessState
from backend.master_router import MasterRouter

st.set_page_config(page_title="NEOVERSE AI OS", page_icon="🌐", layout="wide")

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
    
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def init_os():
    if "state" not in st.session_state:
        st.session_state.state = BusinessState()
        st.session_state.state.update_profile({"industry": "Tech Startup", "location": "Global"})
        st.session_state.state.update_kpis({"revenue": 150000, "business_health": 85})
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "router" not in st.session_state:
        st.session_state.router = MasterRouter()

def render_decision_blocked(result):
    st.markdown("### ⚠️ STAGE 2: KNOWLEDGE GAP DETECTED")
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #ef4444;">
        <h4>MISSING CRITICAL INFORMATION</h4>
        <p><strong>Information Completeness:</strong> {result['stage2'].get('information_completeness')}%</p>
        <p><strong>Missing Variables:</strong> {', '.join(result['stage2'].get('missing_variables', []))}</p>
        <hr>
        <p><i>{result['stage2'].get('interview_question')}</i></p>
    </div>
    """, unsafe_allow_html=True)

def render_decision_complete(result):
    stages = result["stages"]
    
    # 1. Understanding
    st.markdown("### STAGE 1: Business Understanding")
    st.markdown(f"""
    <div class="glass-card">
        <span class="tag">{stages['stage1'].get('business_type')}</span>
        <span class="tag">{stages['stage1'].get('industry')}</span>
        <span class="tag">{stages['stage1'].get('decision_category')}</span>
        <p style="margin-top:10px;">Objective: {stages['stage1'].get('decision_objective')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Assumptions
    st.markdown("### STAGE 3: Assumption Generator")
    assump_html = "".join([f"<li>{a}</li>" for a in stages['stage3'].get('assumptions', [])])
    st.markdown(f'<div class="glass-card"><ul>{assump_html}</ul></div>', unsafe_allow_html=True)
    
    # 4 & 5. Universes & Timeline
    st.markdown("### STAGE 4 & 5: Parallel Universes & Butterfly Effect")
    cols = st.columns(3)
    for i, u in enumerate(stages['stage45'].get('universes', [])):
        with cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="border-top: 3px solid #38bdf8;">
                <h4>{u['name']}</h4>
                <p>Strategy: {u['strategy']}</p>
                <p>Rev Impact: {u['revenue']}</p>
                <hr>
                <small>{'<br>'.join(u['timeline'])}</small>
            </div>
            """, unsafe_allow_html=True)
            
    # 6. Devil's Advocate
    st.markdown("### STAGE 6: Devil's Advocate Engine")
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #ef4444;">
        <p><strong>Why this might fail:</strong> {', '.join(stages['stage6'].get('failure_reasons', []))}</p>
        <p><strong>External Risks:</strong> {', '.join(stages['stage6'].get('external_risks', []))}</p>
        <p>Confidence penalized by Self-Doubt Engine: {stages['stage6'].get('confidence_change_explanation')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 7 & 8. Blind Spots & Opportunities
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### STAGE 7: Blind Spots")
        b_html = "".join([f"<li>{b}</li>" for b in stages['stage7'].get('blind_spots', [])])
        st.markdown(f'<div class="glass-card"><ul>{b_html}</ul></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### STAGE 8: Opportunity Radar")
        o_html = "".join([f"<li>{o['opportunity']} ({o['estimated_impact']})</li>" for o in stages['stage8'].get('opportunities', [])])
        st.markdown(f'<div class="glass-card"><ul>{o_html}</ul></div>', unsafe_allow_html=True)
        
    # 9. Reality Check
    st.markdown("### STAGE 9: Reality Check")
    st.markdown(f"""
    <div class="glass-card">
        <p><strong>Reality Score:</strong> {stages['stage9'].get('reality_score')}/100</p>
        <p><strong>Feasibility:</strong> {stages['stage9'].get('market_feasibility')}</p>
        <p><strong>Explanation:</strong> {stages['stage9'].get('explanation')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 10 & 11. Health & Confidence
    st.markdown("### STAGE 10 & 11: Final Health & Confidence Score")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="metric-value">{stages['stage11'].get('health_score')}</div>
            <p>DECISION HEALTH SCORE</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div class="metric-value">{stages['stage10'].get('overall_confidence')}%</div>
            <p>OVERALL CONFIDENCE</p>
            <small>{stages['stage10'].get('explanation')}</small>
        </div>
        """, unsafe_allow_html=True)
        
    # 12. Final Recommendation
    st.markdown("### STAGE 12: Final Recommendation")
    st.markdown(f"""
    <div class="glass-card" style="border: 1px solid #10b981;">
        <h4 style="color:#10b981;">Best Decision</h4>
        <p>{stages['stage12'].get('best_decision')}</p>
        <hr>
        <h4>Decision to Avoid</h4>
        <p>{stages['stage12'].get('decision_to_avoid')}</p>
        <hr>
        <p><strong>Why:</strong> {stages['stage12'].get('explanation')}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    init_os()
    
    st.markdown('<h1>NEOVERSE <span style="font-weight:300; color:#94a3b8;">OS</span></h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="glass-card" style="border-left:4px solid #38bdf8;"><b>YOU:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            if isinstance(msg["content"], dict):
                # Complex AI response
                if msg["content"]["type"] == "decision_blocked":
                    render_decision_blocked(msg["content"])
                elif msg["content"]["type"] == "decision_complete":
                    render_decision_complete(msg["content"])
            else:
                st.markdown(f'<div class="glass-card" style="border-left:4px solid #10b981;"><b>AI:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            
    user_input = st.chat_input("Input command...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Master AI Router Processing..."):
            result = st.session_state.router.process(user_input, st.session_state.messages, st.session_state.state)
            
        if result["type"] == "chat":
            st.session_state.messages.append({"role": "assistant", "content": result["content"]})
        else:
            st.session_state.messages.append({"role": "assistant", "content": result})
            
        st.rerun()

if __name__ == "__main__":
    main()
