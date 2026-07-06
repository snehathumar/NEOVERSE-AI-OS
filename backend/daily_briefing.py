from backend.llm_client import generate_json
import json

BRIEFING_SCHEMA = {
    "type": "object",
    "properties": {
        "greeting": {"type": "string"},
        "future_watch": {
            "type": "object",
            "properties": {
                "tomorrow": {"type": "string"},
                "seven_days": {"type": "string"},
                "thirty_days": {"type": "string"}
            }
        },
        "learning_insight": {
            "type": "string",
            "description": "If past decisions exist, reference them and explain how they influence today's view."
        }
    },
    "required": ["greeting", "future_watch", "learning_insight"]
}

def generate_daily_briefing_text(business_memory_state: dict, market_signals: dict, radars: dict):
    prompt = f"""
Generate the AI Daily Briefing text based on the following context.
You are an Autonomous AI Business OS that never sleeps.

Business Profile: {business_memory_state.get('profile')}
KPIs: {business_memory_state.get('kpis')}
Past Decisions: {business_memory_state.get('past_decisions', [])}
Today's Market Signals: {json.dumps(market_signals)}
Opportunities & Risks: {json.dumps(radars)}

1. Provide a professional greeting (e.g. "Good Morning. While monitoring your business...")
2. Predict the business trajectory (Future Watch) for Tomorrow, 7 Days, and 30 Days based on momentum.
3. If there are past decisions, extract a 'learning insight' (e.g., "Last month, increasing prices improved revenue by 8%. Based on that...").
"""
    return generate_json(prompt, BRIEFING_SCHEMA)
