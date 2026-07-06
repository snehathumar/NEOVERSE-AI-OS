import time
from typing import Dict

class HealthMonitor:
    """
    Tracks runtime health, latency, and success/failure rates for Models and APIs.
    """
    def __init__(self):
        self.metrics: Dict[str, dict] = {}
        
    def _init_entity(self, entity_id: str):
        if entity_id not in self.metrics:
            self.metrics[entity_id] = {
                "success_count": 0,
                "failure_count": 0,
                "total_latency_ms": 0,
                "status": "Healthy",
                "cooldown_until": 0
            }

    def record_success(self, entity_id: str, latency_ms: float):
        self._init_entity(entity_id)
        self.metrics[entity_id]["success_count"] += 1
        self.metrics[entity_id]["total_latency_ms"] += latency_ms
        self.metrics[entity_id]["status"] = "Healthy"
        
    def record_failure(self, entity_id: str, cooldown_seconds: int = 60):
        self._init_entity(entity_id)
        self.metrics[entity_id]["failure_count"] += 1
        self.metrics[entity_id]["status"] = "Cooldown"
        self.metrics[entity_id]["cooldown_until"] = time.time() + cooldown_seconds

    def is_healthy(self, entity_id: str) -> bool:
        self._init_entity(entity_id)
        if self.metrics[entity_id]["status"] == "Cooldown":
            if time.time() > self.metrics[entity_id]["cooldown_until"]:
                self.metrics[entity_id]["status"] = "Healthy"
                return True
            return False
        return True

    def get_stats(self) -> dict:
        return self.metrics

health_monitor = HealthMonitor()
