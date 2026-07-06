from typing import List
from backend.simulation.models import UniverseOutcome, SensitivityAnalysis
from backend.llm_client import generate_json

class SimulationAnalyzer:
    """
    Analyzes the output of multiple parallel universes to determine Sensitivity and Rank the outcomes.
    """
    def execute(self, universes: List[UniverseOutcome]) -> SensitivityAnalysis:
        prompt = f"""
        You are the NEOVERSE Simulation Analyzer.
        Analyze the following Multi-Universe Simulation outcomes.
        
        Universes: {[u.model_dump() for u in universes]}
        
        Generate a Sensitivity Analysis identifying:
        1. Which variables have the highest impact across universes.
        2. Which assumptions caused the most variance.
        3. What risks amplified the negative universes.
        4. Calculate a Stability Index (0-100) and Decision Robustness Score (0-100).
        """
        
        schema = {
            "type": "object",
            "properties": {
                "most_influential_variables": {"type": "array", "items": {"type": "string"}},
                "most_sensitive_assumptions": {"type": "array", "items": {"type": "string"}},
                "risk_amplifiers": {"type": "array", "items": {"type": "string"}},
                "stability_index": {"type": "integer"},
                "decision_robustness_score": {"type": "integer"}
            },
            "required": ["most_influential_variables", "most_sensitive_assumptions", "risk_amplifiers", "stability_index", "decision_robustness_score"]
        }
        
        res = generate_json(prompt, schema)
        return SensitivityAnalysis(**res)
        
    def rank_universes(self, universes: List[UniverseOutcome]) -> str:
        """
        Rank universes based on ROI, Risk, and Confidence to find the most likely/recommended scenario name.
        """
        # Simple weighted model: 
        # Score = ROI * 0.4 - (FinRisk + OpRisk + MktRisk)*0.1 + Confidence * 0.3
        best_universe = None
        best_score = -float('inf')
        
        for u in universes:
            risk_penalty = (u.financial_risk_score + u.operational_risk_score + u.market_risk_score) / 3.0
            score = (u.roi_estimate * 0.4) - (risk_penalty * 0.1) + (u.confidence * 0.3)
            if score > best_score:
                best_score = score
                best_universe = u.scenario_name
                
        return best_universe if best_universe else universes[0].scenario_name
