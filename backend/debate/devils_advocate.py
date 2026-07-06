from backend.llm_client import generate_json
from backend.debate.models import DevilsAdvocateReport
from typing import List

class DevilsAdvocateEngine:
    """
    Evaluates Black Swans, hidden catastrophic risks, and AI overconfidence.
    Does not vote. Runs strictly to challenge the Round 3 Consensus Defense.
    """
    
    def execute(self, decision_context: dict, final_defenses: List[dict]) -> DevilsAdvocateReport:
        prompt = f"""
        You are the NEOVERSE Devil's Advocate. Your singular purpose is to destroy complacency.
        You must look at the decision context and the final expert defenses and find catastrophic failure modes they missed.
        
        Do not agree. Do not be balanced. Find the hidden, asymmetric risks.
        Look for:
        - Black Swan Events
        - Regulatory Changes
        - Economic Downturns
        - Market Disruption
        - Competitor Reactions
        - Ethical Concerns
        - AI Overconfidence
        - Long-term unintended consequences
        
        Decision Context: {decision_context}
        Expert Defenses: {final_defenses}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "black_swans": {"type": "array", "items": {"type": "string"}},
                "catastrophic_risks": {"type": "array", "items": {"type": "string"}},
                "overconfidence_flags": {"type": "array", "items": {"type": "string"}},
                "missing_evidence": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["black_swans", "catastrophic_risks", "overconfidence_flags", "missing_evidence"]
        }
        
        res = generate_json(prompt, schema)
        return DevilsAdvocateReport(**res)
