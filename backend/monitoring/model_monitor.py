import time
from typing import Dict

class ModelMonitor:
    """
    Monitors Model health score, Success count, Failure count, Cooldown status, Average response time.
    """
    def __init__(self):
        self.model_metrics: Dict[str, dict] = {}
        self.active_model = None

    def _init_model(self, model_name: str):
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = {
                "health_score": 100,
                "success_count": 0,
                "failure_count": 0,
                "total_latency_ms": 0,
                "average_response_time_ms": 0,
                "status": "Ready",
                "cooldown_until": 0
            }

    def set_active_model(self, model_name: str):
        self.active_model = model_name

    def record_success(self, model_name: str, latency_ms: float):
        self._init_model(model_name)
        m = self.model_metrics[model_name]
        m["success_count"] += 1
        m["total_latency_ms"] += latency_ms
        m["average_response_time_ms"] = m["total_latency_ms"] / m["success_count"]
        m["health_score"] = min(100, m["health_score"] + 1)
        m["status"] = "Ready"

    def record_failure(self, model_name: str, cooldown_seconds: int = 120):
        self._init_model(model_name)
        m = self.model_metrics[model_name]
        m["failure_count"] += 1
        m["health_score"] = max(0, m["health_score"] - 20)
        m["status"] = "Cooldown"
        m["cooldown_until"] = time.time() + cooldown_seconds

    def is_healthy(self, model_name: str) -> bool:
        self._init_model(model_name)
        m = self.model_metrics[model_name]
        if m["status"] == "Cooldown":
            if time.time() > m["cooldown_until"]:
                m["status"] = "Ready"
                return True
            return False
        return True

    def get_stats(self) -> dict:
        return {
            "active_model": self.active_model,
            "metrics": self.model_metrics
        }

model_monitor = ModelMonitor()
