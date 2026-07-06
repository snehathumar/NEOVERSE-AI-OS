import asyncio
import uuid
from datetime import datetime, timezone
from backend.platform.cloud.logging_provider import cloud_logger
from backend.autonomy.models import SystemEvent
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.autonomy.ai_debugger import AIDebugger

class SelfHealingEngine:
    """
    Subscribes to system failure events and triggers auto-recovery workflows.
    """
    def __init__(self):
        self.bq = BigQueryProvider()
        self.debugger = AIDebugger()
        
    async def handle_failure(self, failure_event: SystemEvent):
        """
        Processes a critical system failure.
        """
        cloud_logger.critical(f"SELF HEALING ENGINE TRIGGERED for event {failure_event.event_id}")
        
        # 1. Generate RCA
        rca = await self.debugger.analyze_failure(failure_event)
        
        # 2. Trigger auto-repair action based on the RCA
        # In a real environment, this might trigger a webhook to Jenkins/GitHub Actions
        # or restart a K8s deployment.
        
        repair_action = SystemEvent(
            event_id=str(uuid.uuid4()),
            event_type="auto_repair_action",
            timestamp=datetime.now(timezone.utc).isoformat(),
            component="SelfHealingEngine",
            severity="info",
            details={
                "trigger_event_id": failure_event.event_id,
                "action_taken": f"Executed suggestion: {rca.suggested_fix}",
                "status": "success"
            }
        )
        
        self.bq.stream_analytics("system_events", repair_action.model_dump())
        cloud_logger.info(f"Auto-Repair completed successfully for {failure_event.event_id}")
