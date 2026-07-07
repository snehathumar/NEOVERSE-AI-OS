import streamlit as st

st.set_page_config(page_title="NEOVERSE AI | Executive Report", layout="wide")

st.title("📄 Executive AI Report")
st.caption("Module 10: Auto-Generated PDF-Ready Professional Decision Report")

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

from backend.reports.generator import EnterpriseReportGenerator

if st.button("📥 Export as PDF"):
    try:
        report_gen = EnterpriseReportGenerator(output_dir="d:/NEOVERSE AI/exports/reports")
        
        mock_data = {
            "prompt": "Increase Enterprise SaaS pricing by 15%, whilst offering existing customers a 12-month grandfathered rate.",
            "facts": [
                "Competitor pricing is +20% higher on average.",
                "Risk Analysis: Medium risk of churn (est. 4%) mitigated by grandfather clause."
            ],
            "confidence": 89,
            "recommendation": "Increase Enterprise SaaS pricing by 15%, whilst offering existing customers a 12-month grandfathered rate.",
            "universes": {
                "Best Case": "+$1.2M Revenue",
                "Expected Case": "+$950K Revenue",
                "Worst Case": "-$100K Revenue (Demand destruction)"
            }
        }
        
        pdf_path = report_gen.generate_decision_report(decision_id="DEC-Q3-PRICING", data=mock_data)
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=f,
                file_name="Executive_AI_Report.pdf",
                mime="application/pdf"
            )
        st.success(f"Report generated! Click the button above to download.")
    except Exception as e:
        st.error(f"Error generating PDF: {e}")

with st.container():
    st.markdown("<div class='report-container'>", unsafe_allow_html=True)
    
    st.markdown("# Executive Summary: Q3 Pricing Strategy")
    st.markdown("**Date:** 2026-07-04 | **AI Confidence:** 89% (Version 3) | **Status:** Recommendation Finalized")
    
    st.markdown("### 1. The Decision")
    st.markdown("> **Recommendation:** Increase Enterprise SaaS pricing by 15%, whilst offering existing customers a 12-month grandfathered rate.")
    
    st.markdown("### 2. Evidence & Risk")
    st.markdown("""
    - **Market Trend:** Competitor pricing is +20% higher on average.
    - **Risk Analysis:** Medium risk of churn (est. 4%) mitigated by grandfather clause.
    - **Universes Simulated:** 
      - *Best Case:* +$1.2M Revenue
      - *Expected Case:* +$950K Revenue
      - *Worst Case:* -$100K Revenue (Demand destruction)
    """)
    
    st.markdown("### 3. AI Experience & Learning")
    st.markdown("""
    - *In previous similar situations (48 cases analyzed), flat price increases without grandfathering resulted in a 14% spike in churn.*
    - *AI Reasoning Quality Score:* 91.5/100 (High Logic, Low Bias).
    """)
    
    st.markdown("### 4. Future Actions & Monitoring")
    st.markdown("""
    - Monitor daily churn rate via BigQuery.
    - Autonomous trigger set: If churn exceeds 6% in 30 days, AI will automatically trigger a strategy reevaluation.
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)
