import time
from typing import Dict

class APIMonitor:
    """
    Monitors API uptime, Latency, Success rate, Failure rate, Average response time, and Error history.
    """
    def __init__(self):
        self.api_metrics: Dict[str, dict] = {}

    def _init_api(self, api_name: str):
        if api_name not in self.api_metrics:
            self.api_metrics[api_name] = {
                "success_count": 0,
                "failure_count": 0,
                "total_latency_ms": 0,
                "average_response_time_ms": 0,
                "error_history": [],
                "status": "Online"
            }

    def record_success(self, api_name: str, latency_ms: float):
        self._init_api(api_name)
        metrics = self.api_metrics[api_name]
        metrics["success_count"] += 1
        metrics["total_latency_ms"] += latency_ms
        metrics["average_response_time_ms"] = metrics["total_latency_ms"] / metrics["success_count"]
        metrics["status"] = "Online"

    def record_failure(self, api_name: str, error_msg: str):
        self._init_api(api_name)
        metrics = self.api_metrics[api_name]
        metrics["failure_count"] += 1
        metrics["error_history"].append({"timestamp": time.time(), "error": error_msg})
        # Keep last 10 errors
        if len(metrics["error_history"]) > 10:
            metrics["error_history"].pop(0)
        metrics["status"] = "Degraded"

    def get_stats(self) -> dict:
        return self.api_metrics

api_monitor = APIMonitor()
