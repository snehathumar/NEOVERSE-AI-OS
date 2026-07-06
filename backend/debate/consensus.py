from typing import List
from backend.llm_client import generate_json
from backend.debate.models import ConsensusResult, MinorityReport, FinalVote, DevilsAdvocateReport

CONSENSUS_SCHEMA = {
    "type": "object",
    "properties": {
        "majority_opinion": {"type": "string"},
        "consensus_confidence": {"type": "integer"},
        "agreement_score": {"type": "integer"},
        "disagreement_score": {"type": "integer"},
        "minority_report": {
            "type": "object",
            "properties": {
                "dissenting_roles": {"type": "array", "items": {"type": "string"}},
                "opposing_recommendation": {"type": "string"},
                "supporting_evidence": {"type": "array", "items": {"type": "string"}},
                "why_consensus_may_be_wrong": {"type": "string"}
            },
            "required": ["dissenting_roles", "opposing_recommendation", "supporting_evidence", "why_consensus_may_be_wrong"]
        }
    },
    "required": ["majority_opinion", "consensus_confidence", "agreement_score", "disagreement_score"]
}

class ConsensusEngine:
    """
    Calculates Agreement Score, Majority Opinion, and generates Minority Reports.
    """
    
    def execute(self, final_votes: List[FinalVote], devils_advocate: DevilsAdvocateReport) -> ConsensusResult:
        prompt = f"""
        You are the NEOVERSE Consensus Engine.
        Review the final expert votes and the Devil's Advocate report.
        
        Final Votes: {[v.model_dump() for v in final_votes]}
        Devil's Advocate: {devils_advocate.model_dump()}
        
        Your task:
        1. Determine the Majority Opinion.
        2. Calculate the Agreement Score (0-100) and Disagreement Score (0-100).
        3. Determine the Consensus Confidence based on the votes and the Devil's Advocate risks.
        4. If there is significant disagreement, you MUST generate a Minority Report explaining the opposing view, their evidence, and why the consensus might be wrong. If agreement is 100%, omit the minority report.
        """
        
        res = generate_json(prompt, CONSENSUS_SCHEMA)
        
        return ConsensusResult(
            majority_opinion=res["majority_opinion"],
            consensus_confidence=res["consensus_confidence"],
            agreement_score=res["agreement_score"],
            disagreement_score=res["disagreement_score"],
            minority_report=MinorityReport(**res["minority_report"]) if "minority_report" in res and res["minority_report"] else None
        )
