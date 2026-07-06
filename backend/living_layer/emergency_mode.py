from backend.llm_client import generate_json

class EmergencyMode:
    """
    Triggers automatically when a Critical alert (e.g. Revenue Crash) is generated.
    """
    def generate_recovery_plan(self, alert_event: dict, business_state: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "recovery_plan_summary": {"type": "string"},
                "priority_actions": {"type": "array", "items": {"type": "string"}},
                "alternative_strategies": {"type": "array", "items": {"type": "string"}},
                "estimated_recovery_timeline": {"type": "string"}
            },
            "required": ["recovery_plan_summary", "priority_actions", "alternative_strategies", "estimated_recovery_timeline"]
        }
        prompt = f"""
EMERGENCY DETECTED. Generate an immediate Recovery Plan.
Critical Alert: {alert_event}
Business State: {business_state}

Provide immediate priority actions and alternative survival strategies.
"""
        return generate_json(prompt, schema)

emergency_mode = EmergencyMode()
