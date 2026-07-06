from backend.llm_client import generate_json
import json

RECOMMENDATION_ENGINE_SCHEMA = {
    "type": "object",
    "properties": {
        "best_case": {"type": "string"},
        "expected_case": {"type": "string"},
        "worst_case": {"type": "string"},
        "recommendation": {
            "type": "object",
            "properties": {
                "recommended_universe": {"type": "string"},
                "why": {"type": "string"},
                "why_not": {"type": "string"},
                "evidence": {"type": "string"},
                "tradeoffs": {"type": "string"}
            }
        },
        "devils_advocate": {
            "type": "object",
            "properties": {
                "failure_reasons": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    },
    "required": ["best_case", "expected_case", "worst_case", "recommendation", "devils_advocate"]
}

def generate_recommendation_and_critique(decision: str, domain: str, universes: list, assumptions: list):
    prompt = f"""
Decision: "{decision}"
Domain: {domain}
Assumptions: {assumptions}

Universes Simulated:
{json.dumps(universes, indent=2)}

Analyze the simulated universes. Provide an Explainable AI recommendation that details the Best, Expected, and Worst cases.
Identify the recommended universe. Explain why it is the best, why the alternatives were rejected (why not), provide evidence from the simulation, and outline the tradeoffs.
Finally, act as a Devil's Advocate and list reasons why this recommendation could fail.
"""
    return generate_json(prompt, RECOMMENDATION_ENGINE_SCHEMA)
