import json
from datetime import datetime, timezone
from backend.platform.cloud.bigquery_provider import bq_provider
from backend.platform.cloud.logging_provider import cloud_logger

class MemoryAnalyticsEngine:
    """
    Streams Cognitive Memory Analytics to BigQuery.
    """
    def __init__(self):
        pass
        
    def record_retrieval(self, user_id: str, category: str, latency_sec: float, result_count: int):
        """Records retrieval engine performance."""
        bq_provider.insert_rows("memory_retrieval_metrics", [{
            "user_id": user_id,
            "category": category,
            "latency_sec": latency_sec,
            "result_count": result_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }])
        
    def record_learning_effectiveness(self, user_id: str, decision_id: str, confidence_delta: int, success: bool):
        """Records how effectively the AI is learning from previous mistakes."""
        bq_provider.insert_rows("memory_learning_effectiveness", [{
            "user_id": user_id,
            "decision_id": decision_id,
            "confidence_delta": confidence_delta,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }])
        
    def record_memory_growth(self, user_id: str, category: str, size_bytes: int):
        """Records the physical scale of the cognitive memory."""
        bq_provider.insert_rows("memory_growth_metrics", [{
            "user_id": user_id,
            "category": category,
            "size_bytes": size_bytes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }])

memory_analytics = MemoryAnalyticsEngine()
