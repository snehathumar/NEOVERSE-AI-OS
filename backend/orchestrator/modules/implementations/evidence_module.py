from backend.orchestrator.modules.base import ExecutionModule
from backend.evidence.engine import EvidenceTrustEngine
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class EvidenceModule(ExecutionModule):
    """
    Wraps the Phase 9 Enterprise Evidence Trust Engine.
    Executes BEFORE the Decision Engine to validate all facts.
    """
    def __init__(self):
        self.evidence_engine = EvidenceTrustEngine()
        self.bq = BigQueryProvider()
        
    @property
    def name(self) -> str:
        return "EvidenceModule"

    @property
    def is_critical(self) -> bool:
        return True

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Requires user input to perform research against
        return "user_input" in context

    async def execute(self, context: dict) -> dict:
        user_input = context.get("user_input", "")
        # MemoryModule should have already provided the business_state by this point
        business_state = context.get("business_state", {})
        
        evidence_result = await self.evidence_engine.execute_research(user_input, business_state)
        
        # Async stream analytics to BigQuery
        try:
            self.bq.stream_analytics("evidence_sessions", {
                "session_id": context.get("session_id"),
                "total_evidence_collected": len(evidence_result.get("evidence_collected", [])),
                "conflict_reports_count": len(evidence_result.get("conflict_reports", [])),
                "is_sufficient": evidence_result.get("is_sufficient")
            })
        except Exception as e:
            cloud_logger.warning(f"Failed to stream evidence analytics: {e}")
            
        return evidence_result

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
