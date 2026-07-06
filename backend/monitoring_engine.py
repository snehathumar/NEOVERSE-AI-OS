from backend.llm_client import generate_json
import random

MONITORING_SCHEMA = {
    "type": "object",
    "properties": {
        "environmental_state": {
            "type": "object",
            "properties": {
                "weather": {"type": "string"},
                "market_trend": {"type": "string"},
                "fuel_prices": {"type": "string"},
                "competitor_activity": {"type": "string"},
                "consumer_sentiment": {"type": "string"},
                "inflation": {"type": "string"}
            }
        },
        "kpi_impacts": {
            "type": "object",
            "properties": {
                "revenue": {"type": "integer"},
                "costs": {"type": "integer"},
                "business_health": {"type": "integer"}
            },
            "description": "Calculated numeric deltas based on today's events."
        }
    },
    "required": ["environmental_state", "kpi_impacts"]
}

def monitor_environment(profile: dict, kpis: dict, watchlist: list, day: int):
    # Simulate a macro event to keep the environment dynamic
    events = ["None", "Normal Day", "Heavy Storm", "Competitor Discount 20%", "Fuel Price +10%", "Local Festival", "Supply Chain Delay"]
    event_today = random.choice(events)

    prompt = f"""
Simulate the continuous environmental monitoring for Day {day}.
Business Profile: {profile}
Current KPIs: {kpis}
User Watchlist: {watchlist}
Random Simulated Event Today: {event_today}

Generate a realistic snapshot of the environment (weather, market, costs, competition).
Calculate how these specific conditions impact the KPIs today (deltas).

Strictly return JSON matching the schema.
"""
    return generate_json(prompt, MONITORING_SCHEMA)
