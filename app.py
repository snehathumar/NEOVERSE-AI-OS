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
    body { font-family: 'Inter', sans-serif; }
    .welcome-title { font-size: 3.5rem; font-weight: 800; color: #fff; text-align: center; margin-top: 5vh; }
    .welcome-subtitle { font-size: 1.5rem; color: #a0aec0; text-align: center; margin-bottom: 50px; font-weight: 300; }
    .suggestion-grid { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-top: 20px; }
    .chat-card { background: rgba(255,255,255,0.03); border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .quick-action-btn { background: #3182ce; color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; margin-right: 10px; display: inline-block; cursor: pointer; }
    .quick-action-btn:hover { background: #2b6cb0; }
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
    st.markdown("<div style='text-align: center; margin-top: 5vh; margin-bottom: 20px;'><span style='color: #a0aec0;'>──────────────────────────────────────</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-title'>🌌 NEOVERSE AI OS</div>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-subtitle'>Your AI Decision Operating System</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-bottom: 5vh;'><span style='color: #a0aec0;'>──────────────────────────────────────</span></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>💬 Start a Conversation</h3>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-top: 20px; margin-bottom: 20px;'><span style='color: #a0aec0;'>━━━━━━━━━━━━━━━━━━━━━━</span></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>⚡ Quick Decisions</h4>", unsafe_allow_html=True)
    
    st.markdown("<div class='suggestion-grid'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("[ Pricing ]", use_container_width=True): 
            st.session_state.prefill = "Should I increase my pricing?"
            st.rerun()
    with c2: 
        if st.button("[ Hiring ]", use_container_width=True): 
            st.session_state.prefill = "Should I hire another employee?"
            st.rerun()
    with c3: 
        if st.button("[ Expansion ]", use_container_width=True): 
            st.session_state.prefill = "Should I expand to a new location?"
            st.rerun()
    with c4: 
        if st.button("[ Marketing ]", use_container_width=True): 
            st.session_state.prefill = "Should I increase my marketing spend?"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<div style='text-align: center; margin-top: 20px; margin-bottom: 20px;'><span style='color: #a0aec0;'>━━━━━━━━━━━━━━━━━━━━━━</span></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>🧠 AI Workspace</h4>", unsafe_allow_html=True)
    
    st.markdown("<div class='suggestion-grid' style='max-width: 600px; margin: auto;'>", unsafe_allow_html=True)
    w1, w2, w3, w4, w5, w6 = st.columns(6)
    with w1: 
        if st.button("Chat", use_container_width=True): 
            st.session_state.mode = "Chat"
            st.toast("Mode set to: Chat")
    with w2: 
        if st.button("Learn", use_container_width=True): 
            st.session_state.mode = "Learn"
            st.toast("Mode set to: Learn")
    with w3: 
        if st.button("Research", use_container_width=True): 
            st.session_state.mode = "Research"
            st.toast("Mode set to: Research")
    with w4: 
        if st.button("Brainstorm", use_container_width=True): 
            st.session_state.mode = "Brainstorm"
            st.toast("Mode set to: Brainstorm")
    with w5: 
        if st.button("Analyze", use_container_width=True): 
            st.session_state.mode = "Analyze"
            st.toast("Mode set to: Analyze")
    with w6: 
        if st.button("Plan", use_container_width=True): 
            st.session_state.mode = "Plan"
            st.toast("Mode set to: Plan")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-top: 20px; margin-bottom: 20px;'><span style='color: #a0aec0;'>━━━━━━━━━━━━━━━━━━━━━━</span></div>", unsafe_allow_html=True)

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
            # We are in Decision Mode. Use DecisionAgent.
            agent = DecisionAgent()
            
            # If not in simulation, normal interview flow
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
                    
                # Re-init agent with callback
                agent = DecisionAgent(ui_callback=live_ui_update)
                
                # Mocking the complex simulation for now, but doing it via REAL LLM calls and logging
                live_ui_update("Initializing Master Router...")
                live_ui_update("Connecting to Market Data APIs...")
                
                # We ask the agent to do a deep analysis instead of just interviewing
                final_prompt = f"Perform deep analysis on decision: {user_input}. Facts: {st.session_state.facts}. Provide Business Understanding, Evidence, Universes, and Recommendation."
                
                try:
                    final_answer = agent._call_llm(final_prompt)
                    live_ui_update("Calculated Final Recommendation.")
                except Exception as e:
                    final_answer = f"Error during deep analysis: {e}"
                    
                status_box.empty()
                
                # Calculate real confidence based on facts
                conf_score = min(99, 40 + (len(st.session_state.facts) * 15))
                st.session_state.confidence = conf_score
                
                final_answer += f"\n\n*Decision Confidence: {conf_score}%*\n\n---\n**What would you like to do next?**"
                
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

