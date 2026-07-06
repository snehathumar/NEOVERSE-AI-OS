from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ReportMetadata(BaseModel):
    decision_id: str
    session_id: str
    version_number: int
    parent_report_id: Optional[str]
    generation_timestamp: str
    trigger_source: str
    change_summary: Optional[str]
    processing_timeline: Dict[str, float] # ms per stage

class ExplainabilityAudit(BaseModel):
    why_this_recommendation: str
    why_not_alternatives: str
    key_evidence_influence: List[str]
    key_assumptions_made: List[str]
    expert_opinion_shifts: List[str]
    simulation_driving_factor: str
    remaining_uncertainties: List[str]
    audit_trail: Dict[str, Any] # Source scores, votes, etc.

class VisualizationNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any]

class VisualizationEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: Optional[float]

class VisualizationData(BaseModel):
    decision_timeline: List[Dict[str, Any]]
    confidence_timeline: List[Dict[str, Any]]
    risk_matrix: Dict[str, Any]
    opportunity_matrix: Dict[str, Any]
    evidence_heatmap: Dict[str, Any]
    kpi_forecast: List[Dict[str, Any]]
    knowledge_graph: Dict[str, List[Any]] # nodes and edges

class ExecutiveReport(BaseModel):
    id: str
    metadata: ReportMetadata
    executive_summary: str
    business_context: str
    verified_evidence_summary: str
    key_assumptions: str
    decision_analysis: str
    expert_debate_summary: str
    simulation_summary: str
    risk_assessment: str
    opportunity_assessment: str
    financial_impact: str
    kpi_forecast_summary: str
    recommended_action_plan: str
    confidence_metrics: Dict[str, Any]
    explainability: ExplainabilityAudit
    visualizations: VisualizationData
    references: List[str]
