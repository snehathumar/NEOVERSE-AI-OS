from backend.llm_client import generate_json

class ChangeDetector:
    """
    Analyzes raw monitoring data (noise) and categorizes its meaningful impact.
    """
    def detect_change(self, raw_signal: dict, current_business_state: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "is_meaningful": {"type": "boolean"},
                "impact_category": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                "business_impact_summary": {"type": "string"}
            },
            "required": ["is_meaningful", "impact_category", "business_impact_summary"]
        }
        prompt = f"""
Evaluate this incoming market/business signal:
Signal: {raw_signal}
Business State: {current_business_state}

Is this meaningful noise or a real signal? Categorize its impact level.
"""
        return generate_json(prompt, schema)

change_detector = ChangeDetector()
