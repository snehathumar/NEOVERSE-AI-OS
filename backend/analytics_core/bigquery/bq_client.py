import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryClient:
    """
    Central Data Warehouse Client for NEOVERSE AI OS Analytics.
    Handles inserting and querying large-scale analytics data.
    """
    def __init__(self):
        self.project_id = os.environ.get("GCP_PROJECT_ID", "neoverse-ai-os-dev")
        self.dataset_id = "neoverse_analytics"
        
        # In a real environment, we would initialize the client with credentials.
        # For this MVP simulation, we mock the BQ client to prevent crashing if credentials are missing.
        try:
            self.client = bigquery.Client(project=self.project_id)
            self._is_mock = False
            print("✅ [BigQuery] Connected to Google Cloud Data Warehouse.")
        except Exception as e:
            print("⚠️ [BigQuery] Running in Mock/Simulated Mode (No Credentials Found).")
            self._is_mock = True
            self._mock_db = {
                "benchmark_results": [],
                "decision_history": [],
                "performance_metrics": []
            }

    def insert_rows(self, table_name: str, rows: list[dict]):
        if self._is_mock:
            if table_name not in self._mock_db:
                self._mock_db[table_name] = []
            self._mock_db[table_name].extend(rows)
            print(f"📥 [BigQuery-Mock] Inserted {len(rows)} rows into {table_name}")
            return []
            
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
        errors = self.client.insert_rows_json(table_ref, rows)
        if errors:
            print(f"❌ [BigQuery] Failed to insert rows into {table_name}: {errors}")
        return errors

    def query(self, query_string: str):
        if self._is_mock:
            print(f"🔍 [BigQuery-Mock] Simulating query execution.")
            return []
            
        query_job = self.client.query(query_string)
        return query_job.result()

bq_client = BigQueryClient()
