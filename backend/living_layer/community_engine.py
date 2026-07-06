from backend.llm_client import generate_json

class CommunityEngine:
    """
    Community Intelligence Layer.
    Uses simulated anonymized businesses for the MVP.
    """
    def generate_community_insights(self, business_state: dict, decision_type: str) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "similar_businesses_analyzed": {"type": "integer"},
                "most_successful_strategies": {"type": "array", "items": {"type": "string"}},
                "common_mistakes": {"type": "array", "items": {"type": "string"}},
                "average_profit_improvement": {"type": "string"}
            },
            "required": ["similar_businesses_analyzed", "most_successful_strategies", "common_mistakes", "average_profit_improvement"]
        }
        prompt = f"""
Simulate a community intelligence benchmark for {decision_type}.
Business State: {business_state}

Generate insights based on anonymized peer businesses.
"""
        return generate_json(prompt, schema)

community_engine = CommunityEngine()
