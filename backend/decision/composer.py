from typing import Dict, Any
from backend.decision.models import DecisionOutput

class DecisionComposer:
    """
    Step 23: Structured Output Generation.
    Assembles the results of all steps into the strict DecisionOutput schema.
    """
    def execute(self,
                understanding: Dict[str, Any],
                problem: Dict[str, Any],
                evidence: list,
                assumptions: list,
                reasoning: Dict[str, Any],
                risk_opp: Dict[str, Any],
                evaluation: Dict[str, Any],
                explainability: Dict[str, Any],
                trace_ref: str) -> DecisionOutput:
                
        return DecisionOutput(
            executive_summary=explainability["executive_summary"],
            business_understanding=understanding,
            problem_breakdown=problem,
            evidence=evidence,
            missing_information=None,  # We'd have raised MissingInformationException earlier
            assumptions=assumptions,
            risks=risk_opp["risks"],
            opportunities=risk_opp["opportunities"],
            blind_spots=risk_opp["blind_spots"],
            reality_check=evaluation["reality_check"],
            decision_scores=evaluation["decision_scores"],
            confidence_calibration_rationale=evaluation["confidence_calibration_rationale"],
            recommendation=reasoning["recommendation"],
            alternatives=reasoning["alternatives"],
            scenario_planning=reasoning["scenario_planning"],
            self_critique=evaluation["self_critique"],
            next_actions=explainability["next_actions"],
            explainable_ai=explainability["explainable_ai"],
            dependency_graph=explainability["dependency_graph"],
            reasoning_trace_reference=trace_ref
        )
