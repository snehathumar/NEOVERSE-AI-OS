from backend.llm_client import generate_json
import random

MARKET_SIGNAL_SCHEMA = {
    "type": "object",
    "properties": {
        "signals": {
            "type": "object",
            "properties": {
                "Weather": {"type": "string"},
                "Economic Trend": {"type": "string"},
                "Fuel Prices": {"type": "string"},
                "Competitor Activity": {"type": "string"},
                "Consumer Sentiment": {"type": "string"}
            }
        },
        "market_momentum_score": {
            "type": "integer",
            "description": "Score from 0 to 100 indicating overall market momentum for this specific business."
        },
        "kpi_deltas": {
            "type": "object",
            "properties": {
                "revenue": {"type": "integer", "description": "Expected numeric change in revenue based on signals (e.g., -500 or 1200)"},
                "costs": {"type": "integer"},
                "customer_growth": {"type": "number"},
                "business_health": {"type": "integer", "description": "Delta to business health score (e.g. -2 or 3)"}
            }
        }
    },
    "required": ["signals", "market_momentum_score", "kpi_deltas"]
}

def simulate_daily_signals(business_profile: dict, current_kpis: dict, day: int):
    # Introduce random simulated macro events occasionally
    macro_events = ["None", "None", "None", "Heavy Rain", "Festival Weekend", "Heatwave", "Fuel Price Hike", "Local Marathon"]
    event = random.choice(macro_events)
    
    prompt = f"""
Simulate the daily market signals for Day {day}.
Business Profile: {business_profile}
Current KPIs: {current_kpis}
Simulated Macro Event: {event}

Based on the macro event and standard daily fluctuations, generate realistic market signals (Weather, Economy, Competitors).
Calculate a Market Momentum Score (0-100).
Estimate the numerical deltas (changes) to the business KPIs for today based on these signals.
"""
    return generate_json(prompt, MARKET_SIGNAL_SCHEMA)
