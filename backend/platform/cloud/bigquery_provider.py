import os
from typing import Dict, Any, List, Optional
from backend.platform.cloud.logging_provider import cloud_logger
import json
import threading
import atexit
import time
import queue

class BigQueryProvider:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.dataset_id = os.getenv("NEOVERSE_BQ_DATASET", "neoverse_ai")
        self.use_cloud = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
        self.client = None
        
        self._write_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = None

        if self.use_cloud and self.project_id:
            try:
                from google.cloud import bigquery
                self.client = bigquery.Client(project=self.project_id)
                cloud_logger.info(f"BigQuery Provider initialized for dataset: {self.dataset_id}")
                self._start_worker()
            except ImportError:
                cloud_logger.warning("google-cloud-bigquery not installed. Falling back to local logging/no-op.")
            except Exception as e:
                cloud_logger.warning(f"Failed to initialize BigQuery: {e}. Falling back to local logging/no-op.")

    def _start_worker(self):
        if not self._worker_thread:
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()
            atexit.register(self.flush)

    def _worker_loop(self):
        while not self._stop_event.is_set() or not self._write_queue.empty():
            try:
                # Group by table
                batch = {}
                while True:
                    try:
                        table_id, row = self._write_queue.get(timeout=1.0)
                        if table_id not in batch:
                            batch[table_id] = []
                        batch[table_id].append(row)
                    except queue.Empty:
                        break
                
                for table_id, rows in batch.items():
                    if rows:
                        self._sync_insert(table_id, rows)
            except Exception as e:
                cloud_logger.error(f"BQ Worker error: {e}")
                time.sleep(1)

    def flush(self):
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5.0)

    def health_check(self) -> bool:
        if not self.client: return False
        try:
            # simple metadata query
            list(self.client.list_datasets(max_results=1))
            return True
        except Exception:
            return False
    def _sync_insert(self, table_id: str, rows: List[Dict[str, Any]]) -> bool:
        """Synchronously appends rows to BigQuery or falls back to local JSONL."""
        if not rows:
            return True

        if self.client:
            try:
                from tenacity import Retrying, stop_after_attempt, wait_exponential
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)):
                    with attempt:
                        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
                        errors = self.client.insert_rows_json(table_ref, rows)
                        if errors:
                            raise Exception(f"BigQuery insert errors in {table_id}: {errors}")
                return True
            except Exception as e:
                cloud_logger.error(f"Failed to insert into BigQuery {table_id} after retries: {e}. Falling back to local.")

        # Local fallback
        try:
            local_path = self._get_local_file(table_id)
            with open(local_path, "a", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row) + "\n")
            return True
        except Exception as e:
            cloud_logger.error(f"Local BigQuery fallback failed for {table_id}: {e}")
            return False

    def _get_local_file(self, table_id: str) -> str:
        local_dir = os.path.join(os.getcwd(), "data", "bq_fallback")
        os.makedirs(local_dir, exist_ok=True)
        return os.path.join(local_dir, f"{table_id}.jsonl")

    def insert_rows(self, table_id: str, rows: List[Dict[str, Any]]) -> bool:
        """Asynchronously queues rows for BigQuery insertion. Returns True if queued successfully."""
        if not rows: return True
        try:
            for row in rows:
                self._write_queue.put_nowait((table_id, row))
            return True
        except queue.Full:
            cloud_logger.warning("BigQuery write queue full. Falling back to sync insert.")
            return self._sync_insert(table_id, rows)

    def record_decision(self, decision_id: str, outcome: str, reasoning: str):
        self.insert_rows("decision_analytics", [{
            "decision_id": decision_id,
            "outcome": outcome,
            "reasoning": reasoning,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }])

    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        self.insert_rows("monitoring_metrics", [{
            "metric_name": metric_name,
            "value": value,
            "tags": json.dumps(tags or {}),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }])

    def record_agent_execution(self, agent_name: str, duration: float, success: bool):
        self.insert_rows("agent_execution_logs", [{
            "agent_name": agent_name,
            "duration_sec": duration,
            "success": success,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }])

    def record_debate(self, debate_id: str, winner: str, insights: str):
        self.insert_rows("debate_analytics", [{
            "debate_id": debate_id,
            "winner": winner,
            "insights": insights,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }])

bq_provider = BigQueryProvider()
