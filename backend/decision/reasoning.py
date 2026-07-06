from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.decision.models import AlternativeStrategy, ScenarioPlan, AssumptionItem, EvidenceItem

REASONING_SCHEMA = {
    "type": "object",
    "properties": {
        "alternatives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string", 
                        "enum": ["Recommended", "Conservative", "Aggressive", "Low-Cost", "Emergency"]
                    },
                    "description": {"type": "string"},
                    "expected_benefits": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "risks": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "estimated_cost": {"type": "string"},
                    "expected_timeline": {"type": "string"},
                    "confidence": {"type": "integer"}
                },
                "required": ["type", "description", "expected_benefits", "risks", "estimated_cost", "expected_timeline", "confidence"]
            }
        },
        "scenario_planning": {
            "type": "object",
            "properties": {
                "best_case": {"type": "string"},
                "expected_case": {"type": "string"},
                "worst_case": {"type": "string"}
            },
            "required": ["best_case", "expected_case", "worst_case"]
        }
    },
    "required": ["alternatives", "scenario_planning"]
}

class DecisionReasoningEngine:
    """
    Step 12-13, 21: Multi-Step Reasoning, Alternative Generation, and Scenario Planning.
    """
    def execute(self, problem: dict, evidence: List[EvidenceItem], assumptions: List[AssumptionItem]) -> Dict[str, Any]:
        prompt = f"""
        You are the NEOVERSE Decision Reasoning Engine.
        Perform multi-step business reasoning based on the following:
        
        Problem Breakdown: {problem}
        Evidence Provided: {[e.description for e in evidence]}
        Assumptions Made: {[a.description for a in assumptions]}
        
        Your task is to synthesize this into 5 distinct alternative strategies:
        - Recommended
        - Conservative
        - Aggressive
        - Low-Cost
        - Emergency
        
        Additionally, generate Scenario Planning (Best Case, Expected Case, Worst Case) for the Recommended strategy.
        """
        res = generate_json(prompt, REASONING_SCHEMA)
        
        # We ensure all 5 are present or default them safely if LLM misses one (though schema usually enforces it)
        alternatives = [AlternativeStrategy(**alt) for alt in res.get("alternatives", [])]
        scenario = ScenarioPlan(**res.get("scenario_planning", {}))
        
        # We return Recommended strategy separately for easy access, and all alternatives together
        recommended = next((alt for alt in alternatives if alt.type == "Recommended"), None)
        if not recommended and alternatives:
            recommended = alternatives[0]
            
        return {
            "recommendation": recommended,
            "alternatives": alternatives,
            "scenario_planning": scenario
        }
