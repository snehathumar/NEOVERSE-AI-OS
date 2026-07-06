import streamlit as st

st.set_page_config(page_title="NEOVERSE AI | Decision Portfolio", layout="wide")

st.title("📂 Decision Portfolio")
st.caption("Module 9: Enterprise Decision Management & Performance Tracking")

st.markdown("""
<style>
    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 8px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.subheader("Aggregate Portfolio Performance")
c1, c2, c3, c4 = st.columns(4)
c1.markdown("<div class='kpi-card'><h3>All Decisions</h3><h2>1,402</h2></div>", unsafe_allow_html=True)
c2.markdown("<div class='kpi-card'><h3>Success Rate</h3><h2 style='color: #00ff00;'>88.4%</h2></div>", unsafe_allow_html=True)
c3.markdown("<div class='kpi-card'><h3>Avg Confidence</h3><h2>91.2%</h2></div>", unsafe_allow_html=True)
c4.markdown("<div class='kpi-card'><h3>Prediction Accuracy</h3><h2>±4.1%</h2></div>", unsafe_allow_html=True)

st.markdown("---")

t1, t2 = st.tabs(["Top Opportunities", "Top Mistakes"])
with t1:
    st.success("Opportunity 1: Underpriced Enterprise Tier (Expected Revenue +12%)")
    st.success("Opportunity 2: AI Automation in Support (Expected Savings +8%)")
with t2:
    st.error("Mistake 1: Q1 Marketing Spend (ROI was -14% vs Predicted +5%) - *Learning: Weather impact was ignored.*")
    st.error("Mistake 2: Delayed Hiring in Engineering (Resulted in feature delay) - *Learning: Over-indexed on cost savings.*")

st.markdown("---")
st.info("The Decision Portfolio is populated asynchronously from the BigQuery Analytics Engine.")
