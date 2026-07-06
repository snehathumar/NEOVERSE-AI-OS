from backend.orchestrator.modules.base import ExecutionModule
from backend.debate.engine import DebateEngine
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class DebateModule(ExecutionModule):
    """
    Wraps the Phase 7 Enterprise Multi-Agent Decision Validation System.
    """
    def __init__(self):
        self.debate_engine = DebateEngine()
        self.bq = BigQueryProvider()
        
    @property
    def name(self) -> str:
        return "DebateModule"

    @property
    def is_critical(self) -> bool:
        return True

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Require upstream decision output to run debate
        return "DecisionModule" in context.get("upstream_results", {})

    async def execute(self, context: dict) -> dict:
        decision_context = context["upstream_results"]["DecisionModule"]
        
        # We only debate if it's not a missing info trap
        if decision_context.get("is_interview"):
            return {"status": "skipped", "reason": "Decision engine requires interview."}
            
        debate_result = await self.debate_engine.execute_debate(decision_context)
        
        # Async stream analytics to BigQuery
        try:
            self.bq.stream_analytics("debate_sessions", {
                "session_id": context.get("session_id"),
                "expert_panel": debate_result.get("expert_panel"),
                "consensus_confidence": debate_result.get("consensus", {}).get("consensus_confidence"),
                "agreement_score": debate_result.get("consensus", {}).get("agreement_score"),
                "disagreement_score": debate_result.get("consensus", {}).get("disagreement_score"),
                "overall_validation_score": debate_result.get("validation_scores", {}).get("overall_validation_score")
            })
        except Exception as e:
            cloud_logger.warning(f"Failed to stream debate analytics: {e}")
            
        return debate_result

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
