from typing import List
from backend.llm_client import generate_json
from backend.decision.models import AssumptionItem, EvidenceItem

ASSUMPTION_SCHEMA = {
    "type": "object",
    "properties": {
        "assumptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "why_it_exists": {"type": "string"},
                    "confidence": {"type": "integer"},
                    "supporting_evidence": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "risk_if_incorrect": {"type": "string"}
                },
                "required": ["description", "why_it_exists", "confidence", "supporting_evidence", "risk_if_incorrect"]
            }
        }
    },
    "required": ["assumptions"]
}

class AssumptionEngine:
    """
    Step 8-9: Generates explicit assumptions with confidence scoring and risks.
    """
    def execute(self, problem_decomposition: dict, evidence: List[EvidenceItem]) -> List[AssumptionItem]:
        evidence_list = [{"desc": e.description, "trust": e.trust_score} for e in evidence]
        prompt = f"""
        You are the NEOVERSE Assumption Engine.
        Based on the decomposed problem and collected evidence, identify what assumptions we must make to proceed with reasoning.
        
        Problem: {problem_decomposition}
        Evidence: {evidence_list}
        
        Explicitly generate the underlying assumptions. State why each exists, assign a confidence score (0-100) based on the strength of supporting evidence, and detail the risk if this assumption proves incorrect.
        """
        res = generate_json(prompt, ASSUMPTION_SCHEMA)
        return [AssumptionItem(**item) for item in res.get("assumptions", [])]
