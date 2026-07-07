import os
import json
from typing import Optional, Dict, Any
from backend.platform.cloud.logging_provider import cloud_logger

class GCSProvider:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.bucket_name = os.getenv("NEOVERSE_GCS_BUCKET", f"neoverse-ai-storage-{self.project_id}")
        self.use_cloud = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
        self.client = None
        self.bucket = None

        if self.use_cloud and self.project_id:
            try:
                from google.cloud import storage
                self.client = storage.Client(project=self.project_id)
                self.bucket = self.client.bucket(self.bucket_name)
                cloud_logger.info(f"GCS Provider initialized for bucket: {self.bucket_name}")
            except ImportError:
                cloud_logger.warning("google-cloud-storage not installed. Falling back to local storage.")
            except Exception as e:
                cloud_logger.warning(f"Failed to initialize GCS: {e}. Falling back to local storage.")

    def health_check(self) -> bool:
        if not self.bucket: return False
        try:
            self.bucket.exists()
            return True
        except Exception:
            return False

    def _get_local_path(self, blob_name: str) -> str:
        local_dir = os.path.join(os.getcwd(), "data", "storage_fallback")
        os.makedirs(local_dir, exist_ok=True)
        # Flatten the path to prevent directory traversal outside local_dir
        safe_name = blob_name.replace("/", "_").replace("\\", "_")
        return os.path.join(local_dir, safe_name)

    def upload_string(self, blob_name: str, content: str, content_type: str = "text/plain") -> bool:
        """Uploads a string to GCS or falls back to local disk."""
        if self.bucket:
            try:
                from tenacity import Retrying, stop_after_attempt, wait_exponential
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)):
                    with attempt:
                        blob = self.bucket.blob(blob_name)
                        blob.upload_from_string(content, content_type=content_type)
                return True
            except Exception as e:
                cloud_logger.error(f"Failed to upload {blob_name} to GCS: {e}. Falling back to local.")
        
        # Local fallback
        try:
            local_path = self._get_local_path(blob_name)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            cloud_logger.error(f"Local storage fallback failed for {blob_name}: {e}")
            return False

    def upload_file(self, blob_name: str, file_path: str) -> bool:
        """Uploads a file with resumable support and automatic content-type detection."""
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or "application/octet-stream"
        
        if self.bucket:
            try:
                from tenacity import Retrying, stop_after_attempt, wait_exponential
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)):
                    with attempt:
                        blob = self.bucket.blob(blob_name)
                        # upload_from_filename automatically uses resumable uploads for files > 8MB
                        blob.upload_from_filename(file_path, content_type=content_type)
                return True
            except Exception as e:
                cloud_logger.error(f"Failed to upload file {file_path} to {blob_name}: {e}. Falling back to local copy.")

        # Local fallback
        import shutil
        try:
            local_path = self._get_local_path(blob_name)
            shutil.copy2(file_path, local_path)
            return True
        except Exception as e:
            cloud_logger.error(f"Local file fallback failed: {e}")
            return False

    def download_string(self, blob_name: str) -> Optional[str]:
        """Downloads a string from GCS or falls back to local disk."""
        if self.bucket:
            try:
                from tenacity import Retrying, stop_after_attempt, wait_exponential
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)):
                    with attempt:
                        blob = self.bucket.blob(blob_name)
                        if blob.exists():
                            return blob.download_as_string().decode("utf-8")
            except Exception as e:
                cloud_logger.error(f"Failed to download {blob_name} from GCS: {e}. Falling back to local.")

        # Local fallback
        local_path = self._get_local_path(blob_name)
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def upload_pdf(self, filename: str, pdf_bytes: bytes) -> bool:
        if self.bucket:
            try:
                from tenacity import Retrying, stop_after_attempt, wait_exponential
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)):
                    with attempt:
                        blob = self.bucket.blob(f"reports/{filename}")
                        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
                return True
            except Exception as e:
                cloud_logger.error(f"Failed to upload PDF {filename} to GCS: {e}")
        
        # Local fallback
        try:
            local_path = self._get_local_path(f"reports_{filename}")
            with open(local_path, "wb") as f:
                f.write(pdf_bytes)
            return True
        except Exception as e:
            cloud_logger.error(f"Local PDF fallback failed: {e}")
            return False

    def upload_export(self, filename: str, dict_data: Dict[str, Any]) -> bool:
        return self.upload_string(f"exports/{filename}", json.dumps(dict_data, indent=2), "application/json")

    def upload_artifact(self, filename: str, string_data: str) -> bool:
        return self.upload_string(f"artifacts/{filename}", string_data, "text/plain")

    def get_signed_url(self, blob_name: str, expiration_minutes: int = None) -> Optional[str]:
        if not expiration_minutes:
            from backend.platform.cloud.config import cloud_config
            expiration_minutes = cloud_config.signed_url_expiration_minutes
            
        if self.bucket:
            try:
                blob = self.bucket.blob(blob_name)
                if blob.exists():
                    from datetime import timedelta
                    return blob.generate_signed_url(
                        version="v4",
                        expiration=timedelta(minutes=expiration_minutes),
                        method="GET"
                    )
            except Exception as e:
                cloud_logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
        
        # Local fallback - just return the local file path URI
        local_path = self._get_local_path(blob_name)
        if os.path.exists(local_path):
            return f"file://{local_path}"
        return None

gcs_provider = GCSProvider()
