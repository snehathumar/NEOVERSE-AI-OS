import streamlit as st
import pandas as pd
from backend.repositories.decision_repo import DecisionRepository
from backend.platform.storage.models import DecisionState
import time

st.set_page_config(page_title="NEOVERSE AI | Decision Portfolio", layout="wide")

st.title("📂 Decision Portfolio (Human-in-the-Loop)")
st.caption("Enterprise Decision Management, Multi-Level Approval & Performance Tracking")

# Mock RBAC / Current User Profile for demonstration
st.sidebar.header("🔐 RBAC Configuration (Demo)")
current_role = st.sidebar.selectbox("Simulate Role:", ["Director", "Manager", "Team Lead", "Standard User"])
current_user = st.sidebar.text_input("User Name:", "Alice")

user_info = {
    "id": f"usr_{current_user.lower()}",
    "name": current_user,
    "role": current_role,
    "approval_level": "L3" if current_role == "Director" else "L2" if current_role == "Manager" else "L1"
}

repo = DecisionRepository()

# Use session state to force rerenders on approval
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0

try:
    decisions = repo.get_recent_decisions(limit=100)
    total_decisions = len(repo.query())
    avg_confidence = sum([d.get('confidence', 0) for d in decisions]) / max(len(decisions), 1)
    
    # Calculate HITL metrics
    approved_count = len([d for d in decisions if "Approved" in d.get("state", "")])
    override_count = len([d for d in decisions if "Override" in d.get("state", "")])
    approval_rate = (approved_count / total_decisions * 100) if total_decisions > 0 else 0
    override_rate = (override_count / total_decisions * 100) if total_decisions > 0 else 0
except Exception as e:
    decisions = []
    total_decisions = 0
    avg_confidence = 0
    approval_rate = 0
    override_rate = 0
    st.error(f"Failed to connect to Decision Database: {e}")

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

st.subheader("Aggregate Portfolio Performance")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='kpi-card'><h3>All Decisions</h3><h2>{total_decisions}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi-card'><h3>Avg AI Confidence</h3><h2 style='color: #00ff00;'>{avg_confidence:.1f}%</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='kpi-card'><h3>Auto-Approval Rate</h3><h2>{approval_rate:.1f}%</h2></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='kpi-card'><h3>Human Overrides</h3><h2 style='color: #e53e3e;'>{override_rate:.1f}%</h2></div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("Human-in-the-Loop Workflow (HITL)")

if not decisions:
    st.info("No decisions have been made yet.")
else:
    for d in decisions:
        did = d.get('id', 'unknown')
        ts = str(d.get('created_at') or d.get('timestamp') or 'Unknown Date')
        prompt_str = str(d.get('prompt') or 'No Prompt')
        current_state = d.get('state', DecisionState.PENDING_REVIEW.value)
        
        # Determine Badge Class
        badge_class = "badge-Pending"
        if "Approved" in current_state: badge_class = "badge-Approved"
        elif "Override" in current_state: badge_class = "badge-Override"
        elif "Escalated" in current_state: badge_class = "badge-Escalated"
        elif "Rejected" in current_state: badge_class = "badge-Rejected"

        expander_title = f"{ts[:10]} - {prompt_str[:60]}... | State: {current_state}"
        
        with st.expander(expander_title):
            st.markdown(f"<span class='badge {badge_class}'>{current_state}</span>", unsafe_allow_html=True)
            
            st.markdown(f"**Trigger / Prompt:** {prompt_str}")
            
            # Side-by-Side Comparison
            col_ai, col_human = st.columns(2)
            with col_ai:
                st.markdown("<div class='compare-box'>", unsafe_allow_html=True)
                st.markdown(f"### 🤖 AI Recommendation")
                st.markdown(f"**Confidence:** {d.get('confidence')}%")
                st.markdown(d.get('recommendation', 'N/A'))
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col_human:
                st.markdown("<div class='compare-box'>", unsafe_allow_html=True)
                st.markdown(f"### 👤 Human Outcome")
                st.markdown(f"**Final Action:** {d.get('final_human_action', 'Pending')}")
                if d.get('review_comments'):
                    st.markdown(f"**Comments:** {d.get('review_comments')}")
                if d.get('reviewer_name'):
                    st.markdown(f"**Reviewed By:** {d.get('reviewer_name')} ({d.get('reviewer_role')})")
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Interactive Approval Form if pending or escalating
            if current_state in [DecisionState.PENDING_REVIEW.value, DecisionState.ESCALATED.value]:
                st.markdown("#### ⚡ Enterprise Action")
                
                action_col1, action_col2 = st.columns(2)
                
                with action_col1:
                    with st.form(key=f"approve_{did}"):
                        st.markdown("**Approve AI Recommendation**")
                        app_comments = st.text_input("Optional Comments", key=f"ac_{did}")
                        escalate = st.checkbox("Escalate to Next Level", key=f"esc_{did}")
                        submitted_app = st.form_submit_button("Submit Approval", type="primary")
                        
                        if submitted_app:
                            # RBAC Check Mock
                            if current_role == "Standard User" and not escalate:
                                st.error("Standard Users must escalate strategic decisions. RBAC validation failed.")
                            else:
                                new_s = DecisionState.ESCALATED.value if escalate else (DecisionState.APPROVED_WITH_COMMENTS.value if app_comments else DecisionState.APPROVED.value)
                                u_info = dict(user_info)
                                u_info["comment"] = app_comments
                                repo.update_decision_state(did, new_s, u_info)
                                st.session_state.refresh_trigger += 1
                                st.rerun()
                                
                with action_col2:
                    with st.form(key=f"override_{did}"):
                        st.markdown("**Override AI Recommendation**")
                        justification = st.text_area("Mandatory Justification (min 50 chars)", key=f"oj_{did}")
                        hum_conf = st.slider("Human Confidence Score", 0, 100, 80, key=f"hc_{did}")
                        submitted_over = st.form_submit_button("Submit Override")
                        
                        if submitted_over:
                            if len(justification.strip()) < 50:
                                st.error("Validation Error: Overrides must contain a mandatory justification of at least 50 characters.")
                            elif current_role in ["Standard User", "Team Lead"]:
                                st.error("Security Error: Only Managers and Directors can directly override AI core recommendations. Please Escalate instead.")
                            else:
                                u_info = dict(user_info)
                                u_info["comment"] = "Override submitted."
                                repo.update_decision_state(did, DecisionState.OVERRIDE_APPROVED.value, u_info, justification=justification, confidence_score=hum_conf)
                                st.session_state.refresh_trigger += 1
                                st.rerun()
            
            # Approval History Timeline
            history = d.get('approval_history', [])
            if history:
                st.markdown("#### 📜 Immutable Audit Trail")
                for h in history:
                    st.caption(f"🕒 {h.get('reviewed_at', '')[:19].replace('T', ' ')}")
                    st.markdown(f"**{h.get('reviewer_name')}** ({h.get('reviewer_role')}) changed state from `{h.get('previous_state')}` ➔ `{h.get('new_state')}`")
                    if h.get('justification'):
                        st.markdown(f"> *Justification:* {h.get('justification')}")
                    if h.get('comment'):
                        st.markdown(f"> *Comment:* {h.get('comment')}")

st.markdown("---")
st.info(f"Storage Backend: {type(repo.storage).__name__} | Integration: Event Bus & Learning Engine (Active)")
