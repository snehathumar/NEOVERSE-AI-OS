from backend.llm_client import generate_json
import json

ALERT_SCHEMA = {
    "type": "object",
    "properties": {
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "expected_impact": {"type": "string"},
                    "confidence": {"type": "string"},
                    "priority": {"type": "string", "enum": ["High", "Medium", "Low"]}
                }
            }
        },
        "risks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "warning": {"type": "string"},
                    "expected_cost_increase": {"type": "string"},
                    "suggested_actions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "priority": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"]}
                }
            }
        }
    },
    "required": ["opportunities", "risks"]
}

def generate_proactive_alerts(profile: dict, kpis: dict, environmental_state: dict):
    prompt = f"""
Business Profile: {profile}
Current KPIs: {kpis}
Today's Environmental State: {json.dumps(environmental_state)}

You are an Autonomous Business OS. Scan the environment.
Detect hidden Revenue/Cost/Marketing opportunities.
Detect looming Risks (e.g., inflation, weather, supply chain). If the impact is > 5%, raise an alert. Ignore minor < 1% fluctuations.

Return strictly conforming to the JSON schema.
"""
    return generate_json(prompt, ALERT_SCHEMA)
