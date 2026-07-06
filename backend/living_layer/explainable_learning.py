from backend.llm_client import generate_json

class ExplainableLearning:
    """
    Whenever the AI changes its mind, this module generates a clear
    explanation of WHY the confidence and recommendation changed.
    """
    def generate_explanation(self, old_state: dict, new_state: dict, trigger_event: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "confidence_change_reason": {"type": "string"},
                "recommendation_change_reason": {"type": "string"},
                "failed_assumptions": {"type": "array", "items": {"type": "string"}},
                "future_improvement": {"type": "string"}
            },
            "required": ["confidence_change_reason", "recommendation_change_reason", "failed_assumptions", "future_improvement"]
        }
        prompt = f"""
The AI has changed its mind. 
Old State: {old_state}
New State: {new_state}
Trigger Event: {trigger_event}

Explain exactly why the confidence and recommendation changed. Which assumptions failed?
How will this learning improve future predictions?
"""
        return generate_json(prompt, schema)

explainable_learning = ExplainableLearning()
