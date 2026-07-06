from backend.orchestrator.modules.base import ExecutionModule
from backend.reporting.engine import ExecutiveReportingEngine
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger
import time

class ReportGeneratorModule(ExecutionModule):
    """
    Wraps the Phase 10 Enterprise Executive Reporting Engine.
    Executes as the final stage of the pipeline to synthesize outputs.
    """
    def __init__(self):
        self.reporting_engine = ExecutiveReportingEngine()
        self.bq = BigQueryProvider()
        
    @property
    def name(self) -> str:
        return "ReportGeneratorModule"

    @property
    def is_critical(self) -> bool:
        return True

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Requires at least a decision output
        return "DecisionModule" in context.get("upstream_results", {})

    async def execute(self, context: dict) -> dict:
        start_time = time.time()
        
        # We only generate reports if it's a final decision, not a missing info trap
        decision_context = context.get("upstream_results", {}).get("DecisionModule", {})
        if decision_context.get("is_interview"):
            return {"status": "skipped", "reason": "Decision engine requires interview."}
            
        report_result = await self.reporting_engine.execute_reporting(context)
        
        generation_duration = (time.time() - start_time) * 1000
        
        # Async stream analytics to BigQuery
        try:
            self.bq.stream_analytics("reporting_sessions", {
                "session_id": context.get("session_id"),
                "report_id": report_result.get("id"),
                "generation_duration_ms": generation_duration,
                "version_number": report_result.get("metadata", {}).get("version_number")
            })
        except Exception as e:
            cloud_logger.warning(f"Failed to stream reporting analytics: {e}")
            
        return report_result

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
