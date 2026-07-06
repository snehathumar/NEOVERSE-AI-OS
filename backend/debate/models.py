from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ExpertIdentity(BaseModel):
    role: str
    focus: str
    weight: float = 1.0

class InitialOpinion(BaseModel):
    expert_role: str
    stance: str
    supporting_evidence: List[str]
    rejected_assumptions: List[str]
    confidence: int = Field(..., ge=0, le=100)

class CrossExaminationChallenge(BaseModel):
    target_expert: str
    flaws_identified: List[str]
    unsupported_assumptions: List[str]
    hidden_risks: List[str]

class DefenseRevision(BaseModel):
    expert_role: str
    maintained_stance: str
    concessions_made: List[str]
    revised_confidence: int = Field(..., ge=0, le=100)

class FinalVote(BaseModel):
    expert_role: str
    recommendation: str
    confidence: int = Field(..., ge=0, le=100)
    supporting_evidence: List[str]
    remaining_concerns: List[str]
    explainability: str

class DevilsAdvocateReport(BaseModel):
    black_swans: List[str]
    catastrophic_risks: List[str]
    overconfidence_flags: List[str]
    missing_evidence: List[str]

class MinorityReport(BaseModel):
    dissenting_roles: List[str]
    opposing_recommendation: str
    supporting_evidence: List[str]
    why_consensus_may_be_wrong: str

class ConsensusResult(BaseModel):
    majority_opinion: str
    consensus_confidence: int
    agreement_score: int
    disagreement_score: int
    minority_report: Optional[MinorityReport] = None

class ValidationScores(BaseModel):
    consensus_score: int
    debate_strength: int
    evidence_strength: int
    assumption_risk: int
    overall_validation_score: int

class DebateTrace(BaseModel):
    expert_panel: List[str]
    round_1_opinions: List[InitialOpinion]
    round_2_challenges: List[CrossExaminationChallenge]
    round_3_defenses: List[DefenseRevision]
    devils_advocate: DevilsAdvocateReport
    final_votes: List[FinalVote]
    consensus: ConsensusResult
    validation_scores: ValidationScores
    learning_insights: Dict[str, Any]
