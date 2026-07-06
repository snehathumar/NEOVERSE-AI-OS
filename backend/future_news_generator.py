import json
from backend.llm_client import generate_json

FUTURE_NEWS_SCHEMA = {
    "type": "object",
    "properties": {
        "headlines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "headline": {"type": "string"},
                    "date": {"type": "string", "description": "Simulated future date based on the timeline."},
                    "excerpt": {"type": "string", "description": "A one-sentence news snippet."},
                    "sentiment": {"type": "string", "enum": ["Positive", "Negative", "Neutral"]}
                },
                "required": ["headline", "date", "excerpt", "sentiment"]
            },
            "description": "A list of realistic future newspaper headlines."
        }
    },
    "required": ["headlines"]
}

class FutureNewsGenerator:
    """
    Generates realistic future newspaper headlines based on a selected universe
    and business decision. Does not affect the core AI recommendation logic.
    """
    def __init__(self):
        pass

    def generate_news(self, selected_universe: str, business: str, decision: str, timeline: str) -> dict:
        prompt = f"""
You are a Future News Generator.
Your job is to generate realistic newspaper headlines that might appear in the future based on the given business decision and timeline.
The tone and outcome MUST match the characteristics of the Selected Universe. For example, if it's a 'Pessimistic Universe', the headlines should reflect failure or backlash. If it's an 'Aggressive Growth Universe', the headlines should reflect rapid expansion (or chaotic overreach).

Business: "{business}"
Decision Made: "{decision}"
Selected Universe: "{selected_universe}"
Timeline: "{timeline}"

Examples of realistic headlines:
- Revenue Increased by 40% After Bold Pivot
- Store Closed as Customers Protest Price Increase
- Expansion Successful, Market Share Doubles

Generate 3-5 realistic future newspaper headlines, along with simulated future dates, snippets, and sentiment.
Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, FUTURE_NEWS_SCHEMA)
        except Exception as e:
            return {"headlines": [{"headline": "News Generation Failed", "date": "Unknown", "excerpt": str(e), "sentiment": "Neutral"}]}

# Singleton instance
future_news_generator = FutureNewsGenerator()
