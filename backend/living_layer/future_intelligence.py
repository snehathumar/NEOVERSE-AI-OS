from backend.llm_client import generate_json

class FutureIntelligence:
    """
    Generates realistic future scenario timelines.
    """
    def generate_scenarios(self, business_state: dict, decision_context: str) -> list[dict]:
        schema = {
            "type": "object",
            "properties": {
                "timelines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeframe": {"type": "string", "enum": ["7 Days", "30 Days", "6 Months", "1 Year"]},
                            "headline": {"type": "string"},
                            "short_summary": {"type": "string"},
                            "business_impact": {"type": "string"},
                            "confidence": {"type": "integer"}
                        },
                        "required": ["timeframe", "headline", "short_summary", "business_impact", "confidence"]
                    }
                }
            },
            "required": ["timelines"]
        }
        prompt = f"""
Generate future intelligence timelines (7 Days, 30 Days, 6 Months, 1 Year) for this business and decision.
Context: {decision_context}
State: {business_state}
"""
        res = generate_json(prompt, schema)
        return res.get("timelines", [])

future_intelligence = FutureIntelligence()
