from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# --- Module 1: Dependency Graph Models ---
class DependencyNode(BaseModel):
    id: str
    label: str
    category: str = Field(description="e.g., Financial, Operational, Market")

class DependencyEdge(BaseModel):
    source: str
    target: str
    strength: float = Field(description="Impact strength from 0.0 to 1.0")
    description: str

class DecisionGraph(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    critical_nodes: List[str]
    cascading_effects: List[str]

# --- Module 2: Evidence Trust Models ---
class EvidenceSourceScore(BaseModel):
    source_name: str
    reliability_score: int = Field(description="0-100")
    freshness_score: int = Field(description="0-100")
    confidence_contribution: int = Field(description="0-100")
    weight: float

class EvidenceTrustMatrix(BaseModel):
    sources: List[EvidenceSourceScore]
    overall_trust_score: int
    weak_evidence_warnings: List[str]

# --- Module 3: Digital Twin Models ---
class BusinessTwinState(BaseModel):
    revenue: float
    profit: float
    demand: int
    inventory: int
    pricing: float
    employees: int
    customers: int
    marketing_budget: float
    competition_index: int
    cash_flow: float

# --- Module 5: Reasoning Trace Models ---
class ReasoningStep(BaseModel):
    step_name: str
    input_summary: str
    output_summary: str
    confidence: int
    execution_time_ms: int
    evidence_used: List[str]

class ReasoningPipelineTrace(BaseModel):
    decision_id: str
    steps: List[ReasoningStep]
    final_recommendation: str
