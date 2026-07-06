import os
import json
from datetime import datetime, timezone
from backend.cloud_config import cloud_config

class CloudLayer:
    """
    Unified Cloud Layer mapping NEOVERSE components to GCP infrastructure.
    Uses a Graceful Fallback Pattern: if credentials/project_id are missing, 
    it falls back to local disk storage seamlessly without crashing.
    """
    def __init__(self):
        self.project_id = cloud_config.project_id
        
        # We wrap clients so we only instantiate them if available
        self._fs = cloud_config.get_firestore_client() if self.project_id else None
        self._bq = cloud_config.get_bigquery_client() if self.project_id else None
        self._cs = cloud_config.get_storage_client() if self.project_id else None

        # Local fallback dirs
        self.fallback_dir = "backend/local_cloud_fallback"
        if not self.project_id:
            os.makedirs(self.fallback_dir, exist_ok=True)
            print("⚠️ [Cloud Layer] Running in Local Fallback Mode (No GCP credentials).")

    # --- FIRESTORE (User Profiles & Decision History) ---
    def save_user_profile(self, user_id: str, profile_data: dict):
        if self._fs:
            doc_ref = self._fs.collection('user_profiles').document(user_id)
            doc_ref.set(profile_data, merge=True)
        else:
            self._local_save(f"profile_{user_id}.json", profile_data)

    def save_decision_history(self, decision_id: str, history_data: dict):
        if self._fs:
            doc_ref = self._fs.collection('decision_history').document(decision_id)
            doc_ref.set(history_data)
        else:
            self._local_save(f"decision_{decision_id}.json", history_data)

    # --- BIGQUERY (Analytics & Logs) ---
    def log_analytics(self, table_id: str, payload: dict):
        """
        table_id should be in format 'dataset_name.table_name'
        """
        if self._bq:
            try:
                table_ref = self._bq.dataset('neoverse_analytics').table(table_id)
                errors = self._bq.insert_rows_json(table_ref, [payload])
                if errors:
                    print(f"BQ Insert Error: {errors}")
            except Exception as e:
                print(f"BQ Error: {e}")
        else:
            self._local_append(f"bq_mock_{table_id}.jsonl", payload)

    # --- CLOUD STORAGE (Secure Backups & Files) ---
    def backup_data(self, bucket_name: str, destination_blob_name: str, data: str):
        if self._cs:
            try:
                bucket = self._cs.bucket(bucket_name)
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_string(data)
            except Exception as e:
                print(f"GCS Error: {e}")
        else:
            self._local_save(f"gcs_backup_{destination_blob_name.replace('/','_')}.txt", data)

    # --- Local Fallback Helpers ---
    def _local_save(self, filename: str, data):
        path = os.path.join(self.fallback_dir, filename)
        with open(path, 'w') as f:
            if isinstance(data, dict) or isinstance(data, list):
                json.dump(data, f, indent=4)
            else:
                f.write(str(data))
                
    def _local_append(self, filename: str, payload: dict):
        path = os.path.join(self.fallback_dir, filename)
        with open(path, 'a') as f:
            f.write(json.dumps(payload) + "\n")

# Singleton instance
cloud_layer = CloudLayer()
