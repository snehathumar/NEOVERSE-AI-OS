from backend.agents.base_agent import BaseAgent
from backend.llm_client import generate_json

class BrainstormAgent(BaseAgent):
    def handle(self, user_input: str, conversation_history: list, business_state):
        prompt = f"""
You are the Idea Lab of NEOVERSE AI.
The user wants to brainstorm ideas.
Business Profile: {business_state.profile}
User: {user_input}

Generate 3 out-of-the-box, highly strategic ideas. 
Format as a direct response.
Return JSON: {{"response": "markdown formatted ideas"}}
"""
        res = generate_json(prompt, {"type": "object", "properties": {"response": {"type": "string"}}, "required": ["response"]})
        return {"type": "chat", "content": res.get("response", "Here are some ideas...")}
