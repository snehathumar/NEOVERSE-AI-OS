from backend.llm_client import generate_json
import json

DEBATE_SCHEMA = {
    "type": "object",
    "properties": {
        "debate": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "expert": {"type": "string", "enum": ["CEO", "Finance Expert", "Marketing Expert", "Operations Expert", "Customer Success Expert"]},
                    "opinion": {"type": "string"},
                    "stance": {"type": "string", "enum": ["Support", "Oppose", "Neutral"]}
                }
            }
        },
        "final_verdict": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "recommended_universe": {"type": "string"},
                "confidence_score": {"type": "integer"}
            }
        },
        "counter_arguments": {
            "type": "object",
            "properties": {
                "devils_advocate_critique": {"type": "string"},
                "new_risks_found": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "adjusted_confidence_score": {"type": "integer", "description": "Lowered confidence if severe new risks are found."}
            }
        }
    },
    "required": ["debate", "final_verdict", "counter_arguments"]
}

def run_expert_debate(decision: str, domain: str, timelines: list, assumptions: list):
    prompt = f"""
Decision: "{decision}"
Domain: {domain}

Simulated Timelines: {json.dumps(timelines, indent=2)}
Assumptions: {json.dumps(assumptions, indent=2)}

You are simulating an AI Boardroom Debate.
Five experts must independently evaluate the decision and the simulated timelines.
Disagreement is explicitly allowed and encouraged.

Experts:
1. CEO: Focuses on long-term vision and growth.
2. Finance Expert: Focuses on cash flow, ROI, margins.
3. Marketing Expert: Focuses on brand perception and customer acquisition.
4. Operations Expert: Focuses on execution feasibility, supply chain.
5. Customer Success Expert: Focuses on churn, satisfaction, LTV.

After the debate, provide a Final Verdict summarizing the consensus and selecting the recommended Universe (e.g. Universe Alpha), along with a base Confidence Score (0-100).
Then, act as a Devil's Advocate to challenge the Final Verdict. Identify blind spots. If serious new risks are found, output a lower 'adjusted_confidence_score'.

Strictly return JSON.
"""
    return generate_json(prompt, DEBATE_SCHEMA)
