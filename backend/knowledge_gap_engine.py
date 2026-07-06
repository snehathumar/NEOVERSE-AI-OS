from backend.llm_client import generate_json
import json

GAP_SCHEMA = {
    "type": "object",
    "properties": {
        "required_variables": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of core business parameters needed based on the specific domain."
        },
        "missing_variables": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Parameters from the required list that are currently missing from known_data."
        },
        "information_completeness": {
            "type": "integer",
            "description": "Percentage (0-100) of how complete the information is."
        },
        "knowledge_confidence": {
            "type": "string",
            "enum": ["High", "Medium", "Low"],
            "description": "How confident the AI is in the completeness of the context."
        },
        "is_ready_for_recommendation": {
            "type": "boolean",
            "description": "True if completeness is >= 80%, False otherwise."
        },
        "interview_question": {
            "type": "string",
            "description": "If not ready, a natural conversational question asking the user for the missing variables."
        }
    },
    "required": [
        "required_variables", "missing_variables", "information_completeness",
        "knowledge_confidence", "is_ready_for_recommendation", "interview_question"
    ]
}

def analyze_knowledge_gap(decision: str, domain: str, known_data: dict):
    prompt = f"""
You are the Knowledge Gap Engine.
Before making a business decision, you must calculate Information Completeness.
Required information depends heavily on the specific business domain.
For example, a Coffee Shop needs: Current Price, Daily Customers, Monthly Revenue, Competition, Location, Profit Margin.

Decision: "{decision}"
Domain: {domain}
Currently Known Data: {json.dumps(known_data, indent=2)}

Determine the required variables for this domain.
Check which ones are missing.
Calculate Information Completeness (0-100%).
If Information Completeness is < 80%, set 'is_ready_for_recommendation' to false, and formulate a polite, professional interview question to gather the missing data. Do not guess the data.

Strictly return JSON matching the schema.
"""
    return generate_json(prompt, GAP_SCHEMA)
