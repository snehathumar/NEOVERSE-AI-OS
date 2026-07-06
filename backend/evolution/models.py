from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StrategyPattern(BaseModel):
    strategy_id: str
    business_domain: str
    industry: str
    conditions: List[str]
    assumptions: List[str]
    risks: List[str]
    expected_outcome: str
    actual_outcome: Optional[str] = None
    confidence: int = Field(default=50, ge=0, le=100)
    success_rate: int = Field(default=0, ge=0, le=100)
    reusability_score: int = Field(default=50, ge=0, le=100)

class ExpertPerformanceMetrics(BaseModel):
    expert_role: str
    participation_rate: float
    agreement_rate: float
    minority_success_rate: float
    challenge_effectiveness: float
    recommendation_accuracy: float
    confidence_calibration: float
    long_term_performance_trend: str

class SourceReputationMetrics(BaseModel):
    source_name: str
    historical_accuracy: float
    verification_success: float
    bias_trend: float
    freshness: float
    usage_frequency: int
    reliability_score: float

class ConfidenceCalibration(BaseModel):
    predicted_confidence: float
    actual_success: float
    confidence_error: float
    calibration_trend: str

class AIHealthIndex(BaseModel):
    router_health: int
    memory_health: int
    evidence_health: int
    decision_health: int
    debate_health: int
    simulation_health: int
    reporting_health: int
    learning_health: int
    overall_platform_score: int

class LearningEvent(BaseModel):
    learning_id: str
    source_decision_id: str
    trigger: str # e.g. "post_decision", "user_feedback"
    timestamp: str
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    reason: str
    evidence_used: List[str]
    version: int

class EvolutionReport(BaseModel):
    learning_summary: str
    successful_strategies: List[StrategyPattern]
    failed_strategies: List[StrategyPattern]
    confidence_trends: ConfidenceCalibration
    prediction_accuracy: float
    expert_rankings: List[ExpertPerformanceMetrics]
    source_rankings: List[SourceReputationMetrics]
    ai_health: AIHealthIndex
    improvement_recommendations: List[str]
    audit_trail: List[LearningEvent]
