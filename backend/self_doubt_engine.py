from backend.llm_client import generate_json
import json

SELF_DOUBT_SCHEMA = {
    "type": "object",
    "properties": {
        "failure_reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific reasons why this recommendation could fail."
        },
        "missing_evidence": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Critical data points we are assuming but do not actually have."
        },
        "weak_assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Assumptions made that might not hold true."
        },
        "unknown_variables": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Variables in the market or business that are currently completely unknown."
        },
        "market_uncertainty": {
            "type": "string",
            "description": "Analysis of how volatile the current market is."
        },
        "external_risks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Risks outside the control of the business (e.g., weather, regulations)."
        },
        "original_confidence": {
            "type": "integer"
        },
        "recalculated_confidence": {
            "type": "integer",
            "description": "Must be lower than original confidence based on the identified uncertainties."
        },
        "confidence_change_explanation": {
            "type": "string",
            "description": "Detailed explanation of why the confidence was reduced."
        }
    },
    "required": [
        "failure_reasons", "missing_evidence", "weak_assumptions", "unknown_variables", 
        "market_uncertainty", "external_risks", "original_confidence", 
        "recalculated_confidence", "confidence_change_explanation"
    ]
}

def run_self_doubt_analysis(decision: str, recommendation: dict, current_confidence: int):
    prompt = f"""
You are the Self-Doubt Engine.
Your job is to challenge the following AI recommendation and enforce Responsible AI principles.
Never pretend certainty. Never be overconfident. You must actively look for flaws, missing evidence, and external risks.

Original Decision Context: "{decision}"
AI Recommendation: {json.dumps(recommendation, indent=2)}
Current Confidence Score: {current_confidence}%

Challenge your own recommendation. Identify:
1. Unknown risks (failure reasons).
2. Missing evidence.
3. Weak assumptions.
4. Market volatility (market uncertainty).
5. External uncertainty (external risks).

Finally, recalculate the confidence score. You MUST reduce the confidence score to reflect the uncertainty you found. It cannot remain {current_confidence}%. Explain exactly why it was reduced.


Strictly return JSON matching the schema.
"""
    return generate_json(prompt, SELF_DOUBT_SCHEMA)
