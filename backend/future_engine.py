from backend.llm_client import generate_json
import json

FUTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "future_news_headline": {
            "type": "string",
            "description": "A realistic tomorrow's news headline related to this industry or market."
        },
        "opportunity_radar": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Hidden opportunities detected automatically based on the decision context."
        },
        "blind_spot_detector": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Cognitive or strategic blind spots the user might be missing."
        },
        "decision_health_score": {
            "type": "integer",
            "description": "Overall score out of 100 representing the quality, resilience, and data-backing of the decision."
        },
        "regret_meter": {
            "type": "string",
            "description": "Probability of regretting this decision in 6 months (e.g., 'Low - 15%')."
        },
        "reverse_goal_planner": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "action": {"type": "string"}
                }
            },
            "description": "Working backwards from the goal to today."
        }
    },
    "required": ["future_news_headline", "opportunity_radar", "blind_spot_detector", "decision_health_score", "regret_meter", "reverse_goal_planner"]
}

def generate_future_intelligence(decision: str, domain: str, final_verdict: dict):
    prompt = f"""
Decision Context: "{decision}"
Domain: {domain}
Final Verdict Strategy: {json.dumps(final_verdict, indent=2)}

You are the Future Intelligence Layer.
Generate the following:
1. Future News Generator: A realistic headline for tomorrow that could impact this business.
2. Opportunity Radar: Opportunities automatically detected in this specific scenario.
3. Blind Spot Detector: Things the business owner is likely ignoring or biased about.
4. Decision Health Score (0-100): Based on the robustness of the strategy.
5. Regret Meter: The estimated probability of regretting this strategy in 6 months, and why.
6. Reverse Goal Planner: Assuming the strategy succeeds in 1 year, work backwards (Month 12 -> Month 6 -> Month 3 -> Month 1 -> Today) listing the critical actions that must have been taken.

Strictly return JSON matching the schema.
"""
    return generate_json(prompt, FUTURE_SCHEMA)
