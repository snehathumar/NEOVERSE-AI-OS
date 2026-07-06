from backend.llm_client import generate_json
import json

UPDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "did_recommendation_change": {
            "type": "boolean"
        },
        "what_changed": {
            "type": "string",
            "description": "Brief summary of the difference between the old and new recommendation."
        },
        "why_recommendation_changed": {
            "type": "string",
            "description": "Detailed reasoning for the shift in strategy."
        },
        "previous_confidence": {
            "type": "integer"
        },
        "new_confidence": {
            "type": "integer"
        },
        "data_responsible": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The specific new information/data points that caused this change."
        }
    },
    "required": [
        "did_recommendation_change", "what_changed", "why_recommendation_changed",
        "previous_confidence", "new_confidence", "data_responsible"
    ]
}

def compare_and_update_recommendation(previous_recommendation: dict, current_recommendation: dict, new_information: dict):
    prompt = f"""
You are the Recommendation Update Engine.
Your job is to show the evolution of reasoning. Never silently overwrite recommendations.

Previous Recommendation: {json.dumps(previous_recommendation, indent=2)}
Current Recommendation (based on new data): {json.dumps(current_recommendation, indent=2)}
New Information Received: {json.dumps(new_information, indent=2)}

Compare the two recommendations. 
If the core strategy or universe changed (e.g., from Alpha to Beta), explain EXACTLY what changed, why it changed, and which specific piece of new data is responsible for the shift.
If the strategy remains the same but confidence shifted, explain that.

Strictly return JSON matching the schema.
"""
    return generate_json(prompt, UPDATE_SCHEMA)
