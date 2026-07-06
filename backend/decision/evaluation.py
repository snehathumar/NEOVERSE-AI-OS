from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.decision.models import BusinessScores, RiskItem, AlternativeStrategy, AssumptionItem

EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "reality_check": {
            "type": "object",
            "properties": {
                "practical_feasibility": {"type": "string"},
                "budget_feasibility": {"type": "string"},
                "team_capability": {"type": "string"},
                "market_realism": {"type": "string"},
                "timeline_realism": {"type": "string"},
                "is_unrealistic": {"type": "boolean"}
            },
            "required": ["practical_feasibility", "budget_feasibility", "team_capability", "market_realism", "timeline_realism", "is_unrealistic"]
        },
        "self_critique": {
            "type": "object",
            "properties": {
                "what_could_be_wrong": {"type": "string"},
                "weakest_assumptions": {"type": "string"},
                "missing_evidence": {"type": "string"},
                "what_could_change_recommendation": {"type": "string"}
            },
            "required": ["what_could_be_wrong", "weakest_assumptions", "missing_evidence", "what_could_change_recommendation"]
        },
        "business_scores": {
            "type": "object",
            "properties": {
                "decision_quality_score": {"type": "integer"},
                "business_alignment_score": {"type": "integer"},
                "evidence_strength_score": {"type": "integer"},
                "execution_feasibility_score": {"type": "integer"},
                "strategic_impact_score": {"type": "integer"},
                "overall_confidence_score": {"type": "integer"}
            },
            "required": [
                "decision_quality_score", "business_alignment_score", "evidence_strength_score", 
                "execution_feasibility_score", "strategic_impact_score", "overall_confidence_score"
            ]
        },
        "confidence_calibration_rationale": {"type": "string"}
    },
    "required": ["reality_check", "self_critique", "business_scores", "confidence_calibration_rationale"]
}

class EvaluationEngine:
    """
    Step 18-20 & Self-Critique: Reality Check, Business Health Evaluation, and Confidence Calibration.
    """
    def execute(self, recommendation: AlternativeStrategy, risks: List[RiskItem], assumptions: List[AssumptionItem]) -> Dict[str, Any]:
        prompt = f"""
        You are the NEOVERSE Reality Check & Evaluation Engine.
        Critically review the recommended strategy. Do not simply agree with it. Look for flaws.
        
        Recommended Strategy: {recommendation.description}
        Expected Benefits: {recommendation.expected_benefits}
        Identified Risks: {[r.description for r in risks]}
        Weakest Assumptions: {[a.description for a in assumptions if a.confidence < 60]}
        
        Perform the following tasks:
        1. Reality Check: Validate practical, budget, team, and timeline realism. Flag if unrealistic.
        2. AI Self-Critique: What could be wrong? What could change this recommendation?
        3. Business Health Evaluation & Confidence Calibration: Dynamically calculate 6 specific scores (0-100) based on Evidence Coverage, Risk Severity, and Assumption Count. Provide the rationale for the final Overall Confidence Score.
        """
        res = generate_json(prompt, EVALUATION_SCHEMA)
        
        return {
            "reality_check": res.get("reality_check", {}),
            "self_critique": res.get("self_critique", {}),
            "decision_scores": BusinessScores(**res.get("business_scores", {})),
            "confidence_calibration_rationale": res.get("confidence_calibration_rationale", "")
        }
