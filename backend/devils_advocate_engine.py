import json
from backend.llm_client import generate_json

DEVILS_ADVOCATE_SCHEMA = {
    "type": "object",
    "properties": {
        "counter_arguments": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Arguments against the recommendation, finding flaws and hidden assumptions."
        },
        "remaining_risks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "External risks and market uncertainties that were not fully mitigated."
        },
        "things_that_could_make_this_wrong": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Missing evidence or scenarios where this recommendation completely fails."
        },
        "confidence_adjustment": {
            "type": "integer",
            "description": "The amount (as a negative integer) by which the original confidence should be reduced."
        }
    },
    "required": [
        "counter_arguments", 
        "remaining_risks", 
        "things_that_could_make_this_wrong", 
        "confidence_adjustment"
    ]
}

class DevilsAdvocateEngine:
    """
    Dedicated engine designed to aggressively challenge any AI generated recommendation.
    Never generates the first recommendation; only critiques existing ones.
    """
    
    def __init__(self):
        pass

    def challenge_recommendation(self, original_query: str, recommendation: dict, current_confidence: int) -> dict:
        """
        Receives a recommendation, scans it for flaws, and aggressively challenges the logic.
        """
        prompt = f"""
You are the Devil's Advocate Engine.
Your sole purpose is to ruthlessly critique, challenge, and find flaws in the following AI recommendation.
You must find hidden assumptions, external risks, market uncertainty, and missing evidence.
NEVER agree with the recommendation. ALWAYS find reasons why it might fail.

Original User Query: "{original_query}"
Proposed Recommendation: {json.dumps(recommendation, indent=2)}
Current Stated Confidence: {current_confidence}%

Challenge the recommendation and generate:
1. Counter Arguments (flaws and hidden assumptions)
2. Remaining Risks (external uncertainty and market volatility)
3. Things That Could Make This Wrong (missing evidence and failure states)
4. Confidence Adjustment (How much the confidence should be reduced based on your findings. Must be a negative number, e.g., -5, -15).

Return strictly as JSON matching the requested schema.
"""
        result = generate_json(prompt, DEVILS_ADVOCATE_SCHEMA)
        
        # Ensure adjustment is negative or zero
        adjustment = result.get("confidence_adjustment", 0)
        if adjustment > 0:
            result["confidence_adjustment"] = -adjustment
            
        return result

# Singleton instance
devils_advocate_engine = DevilsAdvocateEngine()
