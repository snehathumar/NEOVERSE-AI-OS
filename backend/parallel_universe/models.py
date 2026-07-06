from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class TimelineMilestone(BaseModel):
    timeframe: str = Field(description="e.g., '7 Days', '30 Days', '1 Year'")
    state_description: str
    key_metrics: Dict[str, str] = Field(description="e.g., {'Revenue': '+5%', 'Churn': '-2%'}")
    confidence_score: int

class UniverseScenario(BaseModel):
    universe_type: str = Field(description="Best Case, Most Probable, Conservative, Worst Case, Dynamic Alternative")
    summary: str
    driving_evidence_ids: List[str] = Field(description="List of node IDs from the Evidence Graph")
    assumptions_made: List[str]
    timeline: List[TimelineMilestone] = []
    butterfly_effects: List[str] = []
    future_headlines: List[str] = []
    regret_probabilities: Dict[str, int] = {}
    comparison_scores: Dict[str, int] = {}

class ParallelUniverseSimulation(BaseModel):
    decision_context: str
    universes: List[UniverseScenario]
    recommended_universe: Optional[str] = None
    explainability: Dict[str, str] = {}
