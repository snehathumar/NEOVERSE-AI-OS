import uuid
from datetime import datetime, timezone
from backend.platform.cloud.logging_provider import cloud_logger
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.autonomy.models import ScalingDecision, SystemEvent

class IntelligentScalingController:
    """
    Emits auto-scaling events based on system load.
    Does not directly mutate K8s to maintain strict security boundaries;
    instead relies on HPA custom metrics or CI/CD webhooks.
    """
    def __init__(self):
        self.bq = BigQueryProvider()
        
    def evaluate_scale_action(self, current_cpu_pct: float, current_queue_depth: int):
        """
        Calculates if the system needs to scale up or down.
        Called periodically by the SystemIntelligenceMonitor.
        """
        target = "worker-deployment"
        decision = None
        
        if current_queue_depth > 100 or current_cpu_pct > 80.0:
            decision = ScalingDecision(
                timestamp=datetime.now(timezone.utc).isoformat(),
                target_component=target,
                current_replicas=3, # Mocked
                desired_replicas=10,
                reason=f"High load: CPU {current_cpu_pct}%, Queue {current_queue_depth}"
            )
        elif current_queue_depth == 0 and current_cpu_pct < 20.0:
            decision = ScalingDecision(
                timestamp=datetime.now(timezone.utc).isoformat(),
                target_component=target,
                current_replicas=10, # Mocked
                desired_replicas=3,
                reason="Low load: Scaling down to save costs."
            )
            
        if decision:
            cloud_logger.info(f"Auto-Scale Triggered: {decision.reason} -> Scale {decision.target_component} to {decision.desired_replicas}")
            self._emit_scale_event(decision)
            
    def _emit_scale_event(self, decision: ScalingDecision):
        event = SystemEvent(
            event_id=str(uuid.uuid4()),
            event_type="auto_scale_trigger",
            timestamp=decision.timestamp,
            component="IntelligentScalingController",
            severity="info",
            details=decision.model_dump()
        )
        self.bq.stream_analytics("system_events", event.model_dump())
