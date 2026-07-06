from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.decision.models import RiskItem, OpportunityItem

RISK_OPP_SCHEMA = {
    "type": "object",
    "properties": {
        "risks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["Financial Risk", "Operational Risk", "Market Risk", "Customer Risk", 
                                 "Brand Risk", "Technology Risk", "Legal Risk", "Execution Risk"]
                    },
                    "description": {"type": "string"},
                    "severity": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                    "probability": {"type": "string", "enum": ["Low", "Medium", "High", "Certain"]},
                    "impact": {"type": "string"},
                    "mitigation": {"type": "string"}
                },
                "required": ["category", "description", "severity", "probability", "impact", "mitigation"]
            }
        },
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["Quick Wins", "Long-Term Opportunities", "Hidden Opportunities", "Automation Opportunities", "Competitive Advantages"]
                    },
                    "description": {"type": "string"}
                },
                "required": ["category", "description"]
            }
        },
        "blind_spots": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["risks", "opportunities", "blind_spots"]
}

class RiskOpportunityEngine:
    """
    Step 14-17: Risk Identification, Opportunity Detection, Blind Spot Detection.
    """
    def execute(self, problem: dict, alternatives: List[Any]) -> Dict[str, Any]:
        rec_desc = alternatives[0].description if alternatives else "No recommendation available."
        prompt = f"""
        You are the NEOVERSE Risk & Opportunity Intelligence Engine.
        Analyze the proposed business strategy and its root problem.
        
        Problem: {problem}
        Proposed Strategy: {rec_desc}
        
        Identify:
        1. Comprehensive Risks across the 8 required categories (Financial, Operational, etc.)
        2. Opportunities (Quick wins, hidden edges)
        3. Blind Spots (Ignored assumptions, secondary cascading effects, organizational impacts)
        """
        res = generate_json(prompt, RISK_OPP_SCHEMA)
        
        return {
            "risks": [RiskItem(**r) for r in res.get("risks", [])],
            "opportunities": [OpportunityItem(**o) for o in res.get("opportunities", [])],
            "blind_spots": res.get("blind_spots", [])
        }
