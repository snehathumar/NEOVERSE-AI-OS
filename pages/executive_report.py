import streamlit as st

st.set_page_config(page_title="NEOVERSE AI | Executive Report", layout="wide")

st.title("📄 Executive AI Report")
st.caption("Module 10: Auto-Generated PDF-Ready Professional Decision Report")

st.markdown("""
<style>
    .report-container {
        background-color: white;
        color: black;
        padding: 40px;
        border-radius: 4px;
        font-family: 'Helvetica', sans-serif;
    }
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
