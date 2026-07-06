from backend.agents.base_agent import BaseAgent
from backend.llm_client import generate_json
from backend.learning_engine import log_decision, get_confidence_boost
from backend.community_intelligence import CommunityIntelligenceEngine

class LearningAgent(BaseAgent):
    def handle(self, user_input: str, conversation_history: list, business_state):
        prompt = f"""
You are the Learning Agent.
The user wants to learn, compare historical data, or explore community intelligence.
User: {user_input}

Provide a deep-dive educational response or historical comparison.
Return JSON: {{"response": "markdown response"}}
"""
        res = generate_json(prompt, {"type": "object", "properties": {"response": {"type": "string"}}, "required": ["response"]})
        return {"type": "chat", "content": res.get("response", "Here is the information...")}
