import abc
from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.debate.models import InitialOpinion, CrossExaminationChallenge, DefenseRevision, FinalVote

class BaseExpert(abc.ABC):
    """
    Base expert for the multi-round AI debate system.
    Experts are stateless between rounds, relying strictly on passed context to prevent groupthink.
    """
    
    @property
    @abc.abstractmethod
    def role(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def system_prompt(self) -> str:
        pass

    async def analyze(self, decision_context: dict) -> InitialOpinion:
        """Round 1: Independent Analysis"""
        prompt = f"""
        {self.system_prompt}
        Analyze this decision context completely independently. Do not consider consensus.
        Decision Context: {decision_context}
        """
        # We enforce a dynamic schema for the InitialOpinion
        schema = {
            "type": "object",
            "properties": {
                "stance": {"type": "string"},
                "supporting_evidence": {"type": "array", "items": {"type": "string"}},
                "rejected_assumptions": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "integer"}
            },
            "required": ["stance", "supporting_evidence", "rejected_assumptions", "confidence"]
        }
        res = generate_json(prompt, schema)
        return InitialOpinion(expert_role=self.role, **res)

    async def challenge(self, decision_context: dict, opposing_opinions: List[InitialOpinion]) -> CrossExaminationChallenge:
        """Round 2: Cross Review"""
        prompt = f"""
        {self.system_prompt}
        Review the opposing opinions. Identify flaws, unsupported assumptions, and missing evidence.
        Decision Context: {decision_context}
        Opposing Opinions: {[o.model_dump() for o in opposing_opinions]}
        """
        schema = {
            "type": "object",
            "properties": {
                "target_expert": {"type": "string"},
                "flaws_identified": {"type": "array", "items": {"type": "string"}},
                "unsupported_assumptions": {"type": "array", "items": {"type": "string"}},
                "hidden_risks": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["target_expert", "flaws_identified", "unsupported_assumptions", "hidden_risks"]
        }
        res = generate_json(prompt, schema)
        return CrossExaminationChallenge(**res)

    async def defend(self, my_initial_opinion: InitialOpinion, challenges_against_me: List[CrossExaminationChallenge]) -> DefenseRevision:
        """Round 3: Defense & Revision"""
        prompt = f"""
        {self.system_prompt}
        Defend your position against the attacks made by other experts. Concede where logic dictates.
        My Initial Opinion: {my_initial_opinion.model_dump()}
        Challenges Against Me: {[c.model_dump() for c in challenges_against_me]}
        """
        schema = {
            "type": "object",
            "properties": {
                "maintained_stance": {"type": "string"},
                "concessions_made": {"type": "array", "items": {"type": "string"}},
                "revised_confidence": {"type": "integer"}
            },
            "required": ["maintained_stance", "concessions_made", "revised_confidence"]
        }
        res = generate_json(prompt, schema)
        return DefenseRevision(expert_role=self.role, **res)

    async def vote(self, decision_context: dict, defenses: List[DefenseRevision]) -> FinalVote:
        """Final Vote"""
        prompt = f"""
        {self.system_prompt}
        Based on the full debate defenses, cast your final vote and explain why.
        Final Defenses: {[d.model_dump() for d in defenses]}
        """
        schema = {
            "type": "object",
            "properties": {
                "recommendation": {"type": "string"},
                "confidence": {"type": "integer"},
                "supporting_evidence": {"type": "array", "items": {"type": "string"}},
                "remaining_concerns": {"type": "array", "items": {"type": "string"}},
                "explainability": {"type": "string"}
            },
            "required": ["recommendation", "confidence", "supporting_evidence", "remaining_concerns", "explainability"]
        }
        res = generate_json(prompt, schema)
        return FinalVote(expert_role=self.role, **res)
