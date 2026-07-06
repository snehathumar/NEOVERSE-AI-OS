import uuid
import traceback
from typing import Dict, Any

from backend.decision.understanding import BusinessUnderstandingEngine
from backend.decision.decomposition import ProblemDecompositionEngine
from backend.decision.evidence import EvidenceTrustEngine, MissingInformationException
from backend.decision.assumptions import AssumptionEngine
from backend.decision.reasoning import DecisionReasoningEngine
from backend.decision.risk_opportunities import RiskOpportunityEngine
from backend.decision.evaluation import EvaluationEngine
from backend.decision.explainability import ExplainabilityEngine
from backend.decision.composer import DecisionComposer
from backend.platform.cloud.logging_provider import cloud_logger

class EnterpriseDecisionEngine:
    """
    The Core Reasoning Brain.
    Executes the 23-step decision pipeline sequentially.
    """
    def __init__(self):
        self.understanding = BusinessUnderstandingEngine()
        self.decomposition = ProblemDecompositionEngine()
        self.evidence = EvidenceTrustEngine()
        self.assumptions = AssumptionEngine()
        self.reasoning = DecisionReasoningEngine()
        self.risk_opp = RiskOpportunityEngine()
        self.evaluation = EvaluationEngine()
        self.explainability = ExplainabilityEngine()
        self.composer = DecisionComposer()
        
    async def execute_decision(self, user_input: str, business_state: dict, upstream_results: dict) -> Dict[str, Any]:
        trace_ref = str(uuid.uuid4())
        
        try:
            cloud_logger.info(f"[{trace_ref}] Starting Enterprise Decision Pipeline")
            
            # Step 1-3
            understanding_res = self.understanding.execute(user_input, business_state)
            
            # Step 4
            problem_res = self.decomposition.execute(user_input, understanding_res)
            
            # Step 5-7, 10-11
            # Throws MissingInformationException if critical info is missing (Interview Mode trap)
            evidence_res = self.evidence.execute(user_input, upstream_results, problem_res)
            
            # Step 8-9
            assumptions_res = self.assumptions.execute(problem_res, evidence_res)
            
            # Step 12-13, 21
            reasoning_res = self.reasoning.execute(problem_res, evidence_res, assumptions_res)
            
            # Step 14-17
            risk_opp_res = self.risk_opp.execute(problem_res, reasoning_res["alternatives"])
            
            # Step 18-20
            eval_res = self.evaluation.execute(reasoning_res["recommendation"], risk_opp_res["risks"], assumptions_res)
            
            # Step 22
            expl_res = self.explainability.execute(
                recommendation=reasoning_res["recommendation"].description,
                problem=problem_res,
                alternatives=[a.description for a in reasoning_res["alternatives"]]
            )
            
            # Step 23
            final_output = self.composer.execute(
                understanding=understanding_res,
                problem=problem_res,
                evidence=evidence_res,
                assumptions=assumptions_res,
                reasoning=reasoning_res,
                risk_opp=risk_opp_res,
                evaluation=eval_res,
                explainability=expl_res,
                trace_ref=trace_ref
            )
            
            cloud_logger.info(f"[{trace_ref}] Decision Pipeline completed successfully.")
            return final_output.model_dump()
            
        except MissingInformationException as mie:
            cloud_logger.warning(f"[{trace_ref}] Decision Pipeline entering Interview Mode.")
            return {
                "is_interview": True,
                "missing_information": mie.missing_info
            }
        except Exception as e:
            cloud_logger.error(f"[{trace_ref}] Decision Pipeline failed: {traceback.format_exc()}")
            raise e
