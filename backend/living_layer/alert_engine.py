from backend.llm_client import generate_json

class AlertEngine:
    """
    Generates structured, actionable alerts from meaningful changes.
    """
    def generate_alert(self, detection_event: dict, business_state: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                "reason": {"type": "string"},
                "suggested_action": {"type": "string"},
                "confidence": {"type": "integer"}
            },
            "required": ["priority", "reason", "suggested_action", "confidence"]
        }
        prompt = f"""
Generate a structured alert for this detected change.
Detection: {detection_event}
Business State: {business_state}
"""
        return generate_json(prompt, schema)

alert_engine = AlertEngine()
