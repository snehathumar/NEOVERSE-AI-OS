from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DigitalTwinSnapshot(BaseModel):
    business_profile: Dict[str, str]
    organization_structure: Dict[str, str]
    financial_snapshot: Dict[str, Any]
    operational_kpis: Dict[str, Any]
    market_position: str
    strategic_goals: List[str]
    last_updated: str

class SimulationVariable(BaseModel):
    name: str
    starting_value: float
    ending_value: float
    percentage_change: float

class SimulationDependency(BaseModel):
    source_variable: str
    target_variable: str
    relationship_description: str
    impact_multiplier: float

class UniverseOutcome(BaseModel):
    scenario_name: str
    time_horizon_months: int
    variables: List[SimulationVariable]
    dependencies_triggered: List[SimulationDependency]
    roi_estimate: float
    financial_risk_score: int = Field(..., ge=0, le=100)
    operational_risk_score: int = Field(..., ge=0, le=100)
    market_risk_score: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    data_completeness: int = Field(..., ge=0, le=100)
    assumption_quality: int = Field(..., ge=0, le=100)
    evidence_coverage: int = Field(..., ge=0, le=100)
    prediction_reliability: int = Field(..., ge=0, le=100)
    explanation: Dict[str, str]

class SensitivityAnalysis(BaseModel):
    most_influential_variables: List[str]
    most_sensitive_assumptions: List[str]
    risk_amplifiers: List[str]
    stability_index: int = Field(..., ge=0, le=100)
    decision_robustness_score: int = Field(..., ge=0, le=100)

class SimulationTrace(BaseModel):
    digital_twin: DigitalTwinSnapshot
    universes: List[UniverseOutcome]
    sensitivity_analysis: SensitivityAnalysis
    recommended_scenario: str
    learning_insights: Dict[str, Any]
