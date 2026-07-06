import time
from typing import Callable, Any
from functools import wraps

# Attempt to load prometheus_client; degrade gracefully if not installed in dev
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

if PROMETHEUS_AVAILABLE:
    # 1. API Level Metrics
    HTTP_REQUEST_LATENCY = Histogram(
        'neoverse_http_request_latency_seconds',
        'Latency of HTTP requests in seconds',
        ['method', 'endpoint']
    )
    HTTP_REQUEST_COUNT = Counter(
        'neoverse_http_request_count_total',
        'Total number of HTTP requests',
        ['method', 'endpoint', 'http_status']
    )
    
    # 2. Module Execution Metrics (Enterprise Router)
    MODULE_EXECUTION_LATENCY = Histogram(
        'neoverse_module_execution_latency_seconds',
        'Execution latency per pipeline module',
        ['module_name']
    )
    MODULE_ERROR_COUNT = Counter(
        'neoverse_module_error_count_total',
        'Total number of module execution failures',
        ['module_name']
    )
    
    # 3. AI Workload Metrics (Simulation / Debate)
    SIMULATION_COST = Counter(
        'neoverse_simulation_cost_usd_total',
        'Estimated token cost of digital twin simulations'
    )
    
    # 4. Worker Metrics
    WORKER_QUEUE_DEPTH = Gauge(
        'neoverse_worker_queue_depth',
        'Current number of tasks waiting in the background queue'
    )
    
else:
    # Dummy fallbacks for local dev without prometheus_client installed
    class DummyMetric:
        def labels(self, *args, **kwargs): return self
        def observe(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        
    HTTP_REQUEST_LATENCY = DummyMetric()
    HTTP_REQUEST_COUNT = DummyMetric()
    MODULE_EXECUTION_LATENCY = DummyMetric()
    MODULE_ERROR_COUNT = DummyMetric()
    SIMULATION_COST = DummyMetric()
    WORKER_QUEUE_DEPTH = DummyMetric()

def track_module_execution(module_name: str) -> Callable:
    """
    Decorator to wrap module execution and expose metrics to Prometheus.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time
                MODULE_EXECUTION_LATENCY.labels(module_name=module_name).observe(latency)
                return result
            except Exception as e:
                MODULE_ERROR_COUNT.labels(module_name=module_name).inc()
                raise e
        return wrapper
    return decorator
