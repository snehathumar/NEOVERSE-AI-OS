from backend.agents.base_agent import BaseAgent
from backend.llm_client import generate_json
from backend.future_engine import generate_future_intelligence

class PlanningAgent(BaseAgent):
    def handle(self, user_input: str, conversation_history: list, business_state):
        # We can utilize future_engine's reverse goal planner here
        prompt = f"""
You are the Planning Agent.
The user wants to plan something.
User: {user_input}
Business Profile: {business_state.profile}

Create a reverse-engineered step-by-step roadmap for this goal.
Return JSON: {{"response": "markdown formatted plan"}}
"""
        res = generate_json(prompt, {"type": "object", "properties": {"response": {"type": "string"}}, "required": ["response"]})
        return {"type": "chat", "content": res.get("response", "Here is your plan...")}
