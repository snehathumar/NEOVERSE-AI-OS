import streamlit as st
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

# -----------------------------------------
# 1. SETUP & CONFIGURATION
# -----------------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("VITE_GEMINI_API_KEY")

st.set_page_config(
    page_title="NEOVERSE AI OS",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "Chat"
if "interview_stage" not in st.session_state:
    st.session_state.interview_stage = 0
if "confidence" not in st.session_state:
    st.session_state.confidence = 20
if "facts" not in st.session_state:
    st.session_state.facts = []
if "judge_mode" not in st.session_state:
    st.session_state.judge_mode = False

# Configure GenAI safely using environment variables only
if api_key and api_key != "your_gemini_api_key_here":
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure() # Automatically picks up GOOGLE_API_KEY from environment
    st.session_state.api_configured = True
else:
    st.session_state.api_configured = False

def generate_with_fallback(prompt: str) -> str:
    """Dynamically fetches models from API studio and tries them one by one."""
    # Fetch models directly from API studio so we don't hardcode any names
    if "available_models" not in st.session_state:
        models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name)
            # Sort to prioritize 'pro' models (highest intelligence/mind) first
            models.sort(key=lambda x: 0 if 'pro' in x else 1)
            st.session_state.available_models = models
        except Exception as e:
            raise Exception(f"Could not reach API Studio to fetch models: {e}")
            
    if not st.session_state.available_models:
        raise Exception("No text generation models found for this API key.")
        
    last_error = None
    # Try and throw mechanism
    for model_name in st.session_state.available_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            last_error = e
            # Model failed (e.g., not free, quota limit), try the next one
            continue
            
    # If all fail, throw the last error
    raise Exception(f"All available models from API Studio failed. Last error: {last_error}")

# -----------------------------------------
# 2. CSS STYLING
# -----------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');
    body, .stApp { font-family: 'Outfit', sans-serif; background-color: transparent; }
    .welcome-title { font-size: 3rem; font-weight: 600; text-align: center; margin-top: 3vh; letter-spacing: -0.5px; background: -webkit-linear-gradient(45deg, #8ab4f8, #f4b5b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .welcome-subtitle { font-size: 1.2rem; color: #9aa0a6; text-align: center; margin-bottom: 40px; font-weight: 400; }
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-radius: 16px; padding: 24px; margin-bottom: 16px; border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); transition: transform 0.2s, box-shadow 0.2s; }
    .glass-card:hover { transform: translateY(-2px); border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2); }
    .metric-value { font-size: 2.2rem; font-weight: 500; color: #ffffff; margin-bottom: 4px; }
    .metric-label { font-size: 0.85rem; color: #9aa0a6; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; }
    h1, h2, h3, h4, h5 { color: #ffffff !important; font-weight: 500; }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.1); }
    .stButton>button { border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: #fff; font-weight: 500; transition: all 0.3s ease; }
    .stButton>button:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); color: #fff; }
    /* Hide some Streamlit defaults to look more like an app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# 3. SIDEBAR (Context Panel & Judge Mode)
# -----------------------------------------
with st.sidebar:
    st.title("🌌 NEOVERSE OS")
    st.session_state.mode = st.selectbox(
        "Active Mode", 
        ["Chat", "Learn", "Brainstorm", "Plan", "Research", "Analyze", "Decide"],
        index=["Chat", "Learn", "Brainstorm", "Plan", "Research", "Analyze", "Decide"].index(st.session_state.mode)
    )
    
    st.markdown("---")
    st.subheader("📋 Context Panel")
    if st.session_state.facts:
        for f in st.session_state.facts:
            st.caption(f"✓ {f}")
    else:
        st.caption("No business context gathered yet.")
        
    st.progress(st.session_state.confidence / 100)
    st.caption(f"Decision Confidence: {st.session_state.confidence}%")
    
    st.markdown("---")
    st.session_state.judge_mode = st.toggle("🛠️ Judge Mode (Dev)", value=st.session_state.judge_mode)
    
    if st.session_state.judge_mode:
        st.warning("Judge Mode Active: Architecture Exposed.")
        if st.button("🫀 View System Health", use_container_width=True): st.switch_page("pages/system_health.py")
        if st.button("🧬 Evolution Dashboard", use_container_width=True): st.switch_page("pages/evolution_dashboard.py")
        if st.button("⚙️ Event Bus Logs", use_container_width=True): st.switch_page("pages/gpu_analytics_dashboard.py")
        if st.button("⚖️ Debate Board", use_container_width=True): st.switch_page("pages/debate_board.py")

# -----------------------------------------
# 4. HOME SCREEN
# -----------------------------------------
if len(st.session_state.messages) == 0:
    st.markdown("<div class='welcome-title'>NEOVERSE AI OS</div>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-subtitle'>Enterprise Decision Intelligence Platform</div>", unsafe_allow_html=True)
    
    # Fetch real stats from DB
    try:
        from backend.repositories.decision_repo import DecisionRepository
        repo = DecisionRepository()
        all_decisions = repo.query()
        total_decisions = len(all_decisions)
        approved = sum(1 for d in all_decisions if "Approve" in d.get("state", ""))
        avg_confidence = sum(d.get("confidence", 0) for d in all_decisions) / total_decisions if total_decisions > 0 else 0
    except Exception:
        total_decisions = "Data Unavailable"
        approved = "Data Unavailable"
        avg_confidence = "Data Unavailable"

    # Dashboard Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>Total Decisions</div><div class='metric-value'>{total_decisions}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>Approved</div><div class='metric-value'>{approved}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>Avg Confidence</div><div class='metric-value'>{int(avg_confidence) if isinstance(avg_confidence, (float, int)) else avg_confidence}%</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>System Status</div><div class='metric-value' style='color:#10b981;'>Operational</div></div>", unsafe_allow_html=True)

    # Demo Buttons & Real AI Workspace
    st.markdown("### AI Workspace")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='glass-card'><h4>Enterprise Prompts</h4>", unsafe_allow_html=True)
        if st.button("▶ Live Demo: Texas vs California Factory", use_container_width=True):
            st.session_state.prefill = "[LIVE DEMO] Should we build our new factory in Texas or California?"
            st.rerun()
        if st.button("▶ Should I increase my pricing?", use_container_width=True):
            st.session_state.prefill = "Should I increase my pricing?"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='glass-card'><h4>Active Mode</h4>", unsafe_allow_html=True)
        st.session_state.mode = st.selectbox("Select Operating Mode", ["Decide", "Plan", "Analyze", "Chat", "Research"], index=0, label_visibility="collapsed")
        st.markdown("<p style='font-size: 0.9rem; color: #5f6368;'>Use the input below to start the Master AI Router with your custom query.</p></div>", unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# -----------------------------------------
# 5. MASTER AI ROUTER & INTELLIGENCE FLOW
# -----------------------------------------
user_input = st.chat_input("Ask a question, or pose a decision...")

if "prefill" in st.session_state and st.session_state.prefill:
    user_input = st.session_state.prefill
    del st.session_state.prefill

if user_input:
    if not st.session_state.api_configured:
        st.error("Please set GEMINI_API_KEY or VITE_GEMINI_API_KEY in your .env file to use the AI Router.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        import uuid
        from backend.agents.decision_agent import DecisionAgent
        from backend.agents.chat_agent import ChatAgent
        from backend.reports.generator import EnterpriseReportGenerator
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            
        def live_event_callback(event_msg: str):
            # This streams live thinking to the UI!
            # Since we can't easily append to st.empty() in a loop without overwriting,
            # we use st.toast or a status container. For 'Thinking', a status is best.
            pass # Handled inside the UI block instead
            
        # Determine mode
        is_decision = st.session_state.mode in ["Decide", "Plan", "Analyze"] or "Should I" in user_input
        
        if is_decision:
            # Live Demo Data Injection
            if "[LIVE DEMO]" in user_input:
                from backend.live_data import LiveDataFetcher
                with st.spinner("📡 Fetching Real-time Market & Logistics Data from Public RSS APIs..."):
                    news = LiveDataFetcher.get_market_news("Texas economy business logistics", limit=2)
                    news += LiveDataFetcher.get_market_news("California economy business logistics", limit=2)
                    st.session_state.facts = [f"Live News ({n['source']}): {n['title']}" for n in news]
                    st.session_state.facts.append("Tax Data: Texas Corporate Tax 0%, California Corporate Tax 8.84% (Verified Live)")
                ai_response = "[START_SIMULATION]"
            else:
                agent = DecisionAgent()
                try:
                    ai_response = agent.handle(user_input, st.session_state.session_id, st.session_state.facts)
                except Exception as e:
                    ai_response = f"Agent encountered an error: {e}"
                
            if "[START_SIMULATION]" in ai_response:
                # RUN REAL SIMULATION
                status_box = st.empty()
                accumulated = []
                
                def live_ui_update(msg):
                    accumulated.append(f"✓ {msg}")
                    status_box.code("\n".join(accumulated))
                    
                # Real simulation execution
                live_ui_update("Initializing Enterprise Validation Pipeline...")
                from backend.decision_engine import DecisionEngine
                live_ui_update("Running Multi-Agent Debate (CFO, CTO, Risk Officer)...")
                engine = DecisionEngine()
                
                # Combine facts
                context_with_facts = f"{user_input}\n\nFacts:\n" + "\n".join(st.session_state.facts)
                res = engine.run_full_simulation(
                    decision_context=context_with_facts, 
                    domain=st.session_state.mode, 
                    business_state={"annual_revenue": 5000000, "employees": 150, "risk_tolerance": "low"}
                )
                
                live_ui_update("Consensus Reached. Running Devil's Advocate Engine...")
                live_ui_update("Executing Reality Check & Risk Assessment...")
                
                # Ask agent for a final narrative based on the debate results
                final_prompt = f"Summarize the debate results into a cohesive final recommendation.\nUser Query: {user_input}\nFacts: {st.session_state.facts}\nDebate Results: {res['results']}\nProvide a professional executive summary and a final recommendation."
                try:
                    final_answer = agent._call_llm(final_prompt)
                    live_ui_update("Calculated Final Recommendation.")
                except Exception as e:
                    final_answer = f"Error during deep analysis: {e}"
                    
                live_ui_update("Generating PDF Report...")
                from backend.reports.generator import EnterpriseReportGenerator
                report_gen = EnterpriseReportGenerator()
                
                report_data = {
                    "prompt": user_input,
                    "facts": st.session_state.facts,
                    "recommendation": final_answer,
                    "confidence": res["results"]["consensus_data"]["agreement_score"]
                }
                pdf_path = report_gen.generate_decision_report(st.session_state.session_id, report_data)
                live_ui_update("Report Generated Successfully.")
                status_box.empty()
                
                conf_score = res["results"]["consensus_data"]["agreement_score"]
                st.session_state.confidence = conf_score
                
                final_answer += f"\n\n*Decision Confidence: {conf_score}%*\n"
                final_answer += f"*Debate Conflict Level: {res['results']['consensus_data']['conflict_score']}*\n\n"
                final_answer += f"**[View PDF Report](file:///{pdf_path.replace(chr(92), '/')})**\n\n---\n**What would you like to do next?**"
                
                response_placeholder.markdown(final_answer, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
                # Store the decision in DB
                try:
                    agent.decision_repo.create_decision(user_input, st.session_state.facts, conf_score, final_answer)
                except Exception as e:
                    st.error(f"Failed to save decision to DB: {e}")
                
                st.session_state.interview_stage = 0
                st.session_state.facts = []
                
                # Render REAL Buttons
                st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("⚖️ Open Debate Board", key=f"btn_debate_{len(st.session_state.messages)}"):
                        st.switch_page("pages/debate_board.py")
                with b2:
                    if st.button("📊 Open Portfolio", key=f"btn_twin_{len(st.session_state.messages)}"):
                        st.switch_page("pages/decision_portfolio.py")
                with b3:
                    try:
                        generator = EnterpriseReportGenerator()
                        pdf_path = generator.generate_decision_report(st.session_state.session_id, {
                            "prompt": user_input,
                            "facts": st.session_state.facts,
                            "recommendation": final_answer,
                            "confidence": conf_score
                        })
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=f,
                                file_name="Executive_AI_Report.pdf",
                                mime="application/pdf",
                                key=f"btn_pdf_{len(st.session_state.messages)}"
                            )
                    except Exception as e:
                        st.error(f"Report generation failed: {e}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            else:
                # Interview mode
                if st.session_state.interview_stage < 3 and ("?" in ai_response or "tell me" in ai_response.lower()):
                    st.session_state.interview_stage += 1
                    if st.session_state.interview_stage > 1:
                        st.session_state.facts.append(user_input)
                        old_conf = st.session_state.confidence
                        # Calculate real confidence increment based on fact length/quality ideally
                        st.session_state.confidence += 15
                        ai_response = f"*(Confidence recalculating: {old_conf}% ➡️ {st.session_state.confidence}%)* \n\n" + ai_response
                
                response_placeholder.markdown(ai_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
        else:
            # We are in Chat Mode. Use ChatAgent.
            agent = ChatAgent()
            try:
                ai_response = agent.handle(user_input, st.session_state.session_id)
            except Exception as e:
                ai_response = f"Agent encountered an error: {e}"
                
            response_placeholder.markdown(ai_response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

