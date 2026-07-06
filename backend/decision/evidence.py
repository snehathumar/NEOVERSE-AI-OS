from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.decision.models import EvidenceItem

EVIDENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "evidence_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "trust_score": {"type": "integer"},
                    "freshness": {"type": "string"},
                    "confidence": {"type": "integer"},
                    "bias_indicator": {"type": "string"},
                    "verification_status": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["source", "trust_score", "freshness", "confidence", "bias_indicator", "verification_status", "description"]
            }
        },
        "is_missing_critical_info": {"type": "boolean"},
        "missing_information": {
            "type": "object",
            "properties": {
                "missing_fields": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "importance": {"type": "string"},
                "reason": {"type": "string"},
                "suggested_follow_up_questions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["missing_fields", "importance", "reason", "suggested_follow_up_questions"]
        }
    },
    "required": ["evidence_items", "is_missing_critical_info"]
}

class MissingInformationException(Exception):
    def __init__(self, missing_info: Dict[str, Any]):
        self.missing_info = missing_info
        super().__init__(f"Critical Information Missing: {missing_info.get('missing_fields')}")

class EvidenceTrustEngine:
    """
    Step 5-7, 10-11: Evidence Collection, Trust Scoring, Missing Info Detection.
    Receives injected external context from the Router (Memory, Documents, Tool Outputs).
    """
    def execute(self, user_input: str, router_context: Dict[str, Any], decomposition: Dict[str, Any]) -> List[EvidenceItem]:
        prompt = f"""
        You are the NEOVERSE Enterprise Evidence Engine.
        Your task is to analyze the injected context provided by the Router and assign strict Trust Scores to every piece of evidence.
        
        User Request: "{user_input}"
        Decomposed Problem: {decomposition}
        Injected Router Context: {router_context}
        
        Evaluate the injected context.
        If critical evidence is missing to confidently reason about the root causes or dependencies, set 'is_missing_critical_info' to true and fill out 'missing_information'.
        Otherwise, extract all evidence items, assigning Trust Score (0-100), Freshness, Confidence (0-100), Bias Indicator, and Verification Status.
        """
        
        res = generate_json(prompt, EVIDENCE_SCHEMA)
        
        if res.get("is_missing_critical_info") and res.get("missing_information"):
            # Trigger Router Interview Mode
            raise MissingInformationException(res["missing_information"])
            
        return [EvidenceItem(**item) for item in res.get("evidence_items", [])]
