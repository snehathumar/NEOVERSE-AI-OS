import uuid
from datetime import datetime, timezone
from backend.platform.cloud.logging_provider import cloud_logger
from backend.autonomy.models import SystemEvent
from backend.platform.cloud.bigquery_provider import BigQueryProvider

class CostOptimizationEngine:
    """
    Monitors infrastructure spend and emits warnings if budgets are exceeded.
    """
    def __init__(self):
        self.bq = BigQueryProvider()
        
    def evaluate_cost_efficiency(self, token_spend: float, compute_spend: float):
        """
        Calculates if the system is operating within budget.
        """
        budget_limit = 1000.0 # Mocked
        current_spend = token_spend + compute_spend
        
        if current_spend > budget_limit:
            cloud_logger.warning(f"BUDGET EXCEEDED: Current spend ${current_spend} > Budget ${budget_limit}")
            event = SystemEvent(
                event_id=str(uuid.uuid4()),
                event_type="system_warning",
                timestamp=datetime.now(timezone.utc).isoformat(),
                component="CostOptimizationEngine",
                severity="warning",
                details={
                    "reason": "budget_exceeded",
                    "current_spend": current_spend,
                    "budget_limit": budget_limit,
                    "recommended_action": "trigger_scale_down"
                }
            )
            self.bq.stream_analytics("system_events", event.model_dump())
