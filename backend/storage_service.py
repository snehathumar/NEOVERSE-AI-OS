from backend.cloud_config import cloud_config
import datetime
from google.cloud import storage

class StorageService:
    """
    Dedicated Storage Service for interacting with Google Cloud Storage.
    Handles uploading files and generating Signed URLs.
    """
    
    def __init__(self, bucket_name="neoverse_storage_bucket"):
        self.bucket_name = bucket_name
        self._client = None

    @property
    def gcs(self):
        if self._client is None:
            self._client = cloud_config.get_storage_client()
        return self._client

    def _ensure_bucket(self):
        """Creates the bucket if it does not exist."""
        try:
            bucket = self.gcs.get_bucket(self.bucket_name)
        except Exception:
            # If bucket not found, attempt to create it
            bucket = self.gcs.bucket(self.bucket_name)
            bucket.location = cloud_config.location
            bucket = self.gcs.create_bucket(bucket)
        return bucket

    def _generate_signed_url(self, blob_name: str, expiration_minutes: int = 60) -> str:
        """
        Generates a v4 signed URL for downloading a blob.
        Note: Requires proper service account credentials with signing permissions.
        """
        bucket = self.gcs.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=expiration_minutes),
            method="GET",
        )
        return url

    def _upload_file(self, folder: str, filename: str, file_bytes: bytes, content_type: str) -> str:
        """Internal helper to upload bytes to a specific folder and return a signed URL."""
        bucket = self._ensure_bucket()
        blob_name = f"{folder}/{filename}"
        blob = bucket.blob(blob_name)
        
        blob.upload_from_string(file_bytes, content_type=content_type)
        return self._generate_signed_url(blob_name)

    # -------------------------------------------------------------------------
    # Reusable Upload Functions for Specific Asset Types
    # -------------------------------------------------------------------------
    
    def upload_pdf_report(self, filename: str, pdf_bytes: bytes) -> str:
        """Uploads a PDF report and returns a temporary signed URL."""
        return self._upload_file("reports/pdf", filename, pdf_bytes, "application/pdf")

    def upload_chart(self, filename: str, image_bytes: bytes, image_type: str = "png") -> str:
        """Uploads a generated chart and returns a temporary signed URL."""
        content_type = f"image/{image_type}"
        return self._upload_file("charts", filename, image_bytes, content_type)

    def upload_csv_export(self, filename: str, csv_bytes: bytes) -> str:
        """Uploads a CSV export and returns a temporary signed URL."""
        return self._upload_file("exports/csv", filename, csv_bytes, "text/csv")

    def upload_user_file(self, user_id: str, filename: str, file_bytes: bytes, content_type: str) -> str:
        """Uploads a file provided by the user, segmented by user_id."""
        folder = f"uploads/{user_id}"
        return self._upload_file(folder, filename, file_bytes, content_type)

    def upload_future_report(self, decision_id: str, filename: str, report_bytes: bytes) -> str:
        """Uploads an AI generated future intelligence report."""
        folder = f"reports/future/{decision_id}"
        return self._upload_file(folder, filename, report_bytes, "application/pdf")

# Singleton instance
storage_service = StorageService()
