import time

class PerformanceTracker:
    """
    Application Performance Monitoring (APM).
    Tracks execution times across all domains to identify bottlenecks.
    """
    def __init__(self):
        self.metrics = []

    def track(self, module_name: str, execution_time_ms: float):
        record = {
            "module": module_name,
            "execution_time_ms": execution_time_ms,
            "timestamp": time.time()
        }
        self.metrics.append(record)
        
    def generate_optimization_suggestions(self) -> list:
        suggestions = []
        for m in self.metrics:
            if m["execution_time_ms"] > 1000:
                suggestions.append(f"⚠️ Bottleneck in {m['module']} (Took {m['execution_time_ms']}ms). Consider caching or GPU acceleration.")
        return suggestions

performance_tracker = PerformanceTracker()
