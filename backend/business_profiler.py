from backend.llm_client import generate_json

BUSINESS_PROFILER_SCHEMA = {
    "type": "object",
    "properties": {
        "profile": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "current_price": {"type": "string"},
                "daily_customers": {"type": "string"},
                "monthly_revenue": {"type": "string"},
                "competitors": {"type": "string"},
                "profit_margin": {"type": "string"}
            }
        },
        "missing_critical_data": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["profile", "missing_critical_data"]
}

class BusinessProfiler:
    def __init__(self):
        self.profile = {}
        
    def update_profile_from_conversation(self, conversation_history: list):
        history_str = "Conversation History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-10:]])
        
        prompt = f"""
Analyze the conversation history and extract any business profile parameters mentioned by the user.
Update the profile with known values. If a critical value (domain, price, customers, revenue, competitors, margin) is still missing, list it in 'missing_critical_data'.

{history_str}
"""
        result = generate_json(prompt, BUSINESS_PROFILER_SCHEMA)
        if not result.get("error"):
            # Update existing profile with new non-null values
            for k, v in result.get("profile", {}).items():
                if v and v.strip():
                    self.profile[k] = v
        return result
