import time
from typing import Dict, Any

class SystemObservability:
    """
    Tracks Latency, Errors, Tool Usage, GPU Usage, and Token Metrics.
    Listens to the Event Bus to avoid blocking the main execution path.
    """
    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "errors": 0,
            "gpu_fallbacks": 0,
            "total_latency_ms": 0,
            "decisions_processed": 0
        }
        
    def log_latency(self, module: str, latency_ms: float):
        self.metrics["total_latency_ms"] += latency_ms
        print(f"📊 [Observability] {module} completed in {latency_ms:.2f}ms")

    def log_error(self, module: str, error: str):
        self.metrics["errors"] += 1
        print(f"🚨 [Observability] ERROR in {module}: {error}")
        
    def log_api_call(self, tool_name: str):
        self.metrics["api_calls"] += 1
        
    def get_health_report(self) -> Dict[str, Any]:
        return self.metrics

system_observability = SystemObservability()
