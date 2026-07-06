from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Core Primitive Types ---

class EvidenceItem(BaseModel):
    source: str
    trust_score: int = Field(..., ge=0, le=100)
    freshness: str
    confidence: int = Field(..., ge=0, le=100)
    bias_indicator: str
    verification_status: str
    description: str

class AssumptionItem(BaseModel):
    description: str
    why_it_exists: str
    confidence: int = Field(..., ge=0, le=100)
    supporting_evidence: List[str]
    risk_if_incorrect: str

class RiskItem(BaseModel):
    category: str  # Financial, Operational, Market, etc.
    description: str
    severity: str
    probability: str
    impact: str
    mitigation: str

class OpportunityItem(BaseModel):
    category: str
    description: str

class AlternativeStrategy(BaseModel):
    type: str # Recommended, Conservative, Aggressive, Low-Cost, Emergency
    description: str
    expected_benefits: List[str]
    risks: List[str]
    estimated_cost: str
    expected_timeline: str
    confidence: int = Field(..., ge=0, le=100)

class DependencyNode(BaseModel):
    id: str
    label: str
    type: str

class DependencyEdge(BaseModel):
    source: str
    target: str
    impact_level: str

class DependencyGraph(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]

class BusinessScores(BaseModel):
    decision_quality_score: int
    business_alignment_score: int
    evidence_strength_score: int
    execution_feasibility_score: int
    strategic_impact_score: int
    overall_confidence_score: int

class ScenarioPlan(BaseModel):
    best_case: str
    expected_case: str
    worst_case: str

class MissingInformationFlag(BaseModel):
    missing_fields: List[str]
    importance: str
    reason: str
    suggested_follow_up_questions: List[str]

# --- Master Output Schema ---

class DecisionOutput(BaseModel):
    executive_summary: str
    business_understanding: Dict[str, str]
    problem_breakdown: Dict[str, List[str]]
    evidence: List[EvidenceItem]
    missing_information: Optional[MissingInformationFlag] = None
    assumptions: List[AssumptionItem]
    risks: List[RiskItem]
    opportunities: List[OpportunityItem]
    blind_spots: List[str]
    reality_check: Dict[str, str]
    decision_scores: BusinessScores
    confidence_calibration_rationale: str
    recommendation: AlternativeStrategy
    alternatives: List[AlternativeStrategy]
    scenario_planning: ScenarioPlan
    self_critique: Dict[str, str]
    next_actions: List[str]
    explainable_ai: Dict[str, str]
    dependency_graph: DependencyGraph
    reasoning_trace_reference: str
