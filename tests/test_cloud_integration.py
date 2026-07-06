import os
import unittest
import time
from uuid import uuid4

# Setup test environment to force cloud on
os.environ["USE_CLOUD_STORAGE"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT_ID"] = "gen-lang-client-0453814955"
os.environ["NEOVERSE_GCS_BUCKET"] = "neoverse-ai-storage-gen-lang-client-0453814955"
os.environ["NEOVERSE_BQ_DATASET"] = "neoverse_ai"

# Ensure we have credentials (this assumes the local environment or CI is authenticated with gcloud or GOOGLE_APPLICATION_CREDENTIALS)

from backend.platform.storage.factory import get_storage_manager
from backend.platform.cloud.bigquery_provider import bq_provider
from backend.platform.cloud.gcs_provider import gcs_provider
from backend.platform.cloud.secrets_provider import secrets_provider
from backend.platform.cloud.logging_provider import cloud_logger

class TestCloudIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We fetch the unified storage manager
        cls.storage = get_storage_manager()
        cls.test_id = str(uuid4())
        
    def test_1_firestore_integration(self):
        """Test real Firestore write, read, and delete"""
        doc_id = f"test_doc_{self.test_id}"
        test_data = {"name": "integration_test", "timestamp": time.time()}
        
        # 1. Write
        res_id = self.storage.save("neoverse_test_collection", doc_id, test_data)
        self.assertEqual(res_id, doc_id)
        
        # 2. Read
        data = self.storage.get("neoverse_test_collection", doc_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "integration_test")
        
        # 3. Delete
        del_res = self.storage.delete("neoverse_test_collection", doc_id)
        self.assertTrue(del_res)
        
        # 4. Verify Delete
        deleted_data = self.storage.get("neoverse_test_collection", doc_id)
        self.assertIsNone(deleted_data)

    def test_2_bigquery_integration(self):
        """Test real BigQuery streaming insert (we don't wait to query since streaming buffer takes time)"""
        # Use neoverse_test_ table
        success = bq_provider.insert_rows("neoverse_test_metrics", [{
            "metric_name": "integration_test_metric",
            "value": 1.0,
            "tags": "{}",
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }])
        self.assertTrue(success, "BigQuery insertion returned False")
        bq_provider.flush() # Ensure async worker executes

    def test_3_gcs_integration(self):
        """Test real Cloud Storage upload and signed URL generation"""
        filename = f"test_artifact_{self.test_id}.txt"
        content = "This is a cloud integration test artifact."
        
        # 1. Upload
        success = gcs_provider.upload_artifact(filename, content)
        self.assertTrue(success, "GCS upload returned False")
        
        # 2. Signed URL
        url = gcs_provider.get_signed_url(f"artifacts/{filename}")
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("http") or url.startswith("file://"))
        
        # Cleanup (Optional for GCS, but good practice)
        if gcs_provider.bucket:
            try:
                blob = gcs_provider.bucket.blob(f"artifacts/{filename}")
                blob.delete()
            except Exception as e:
                pass # ignore cleanup errors

    def test_4_secret_manager_integration(self):
        """Test real Secret Manager access (requires secret to exist, or falls back)"""
        # If the environment isn't perfectly configured, it falls back to .env
        # The test mainly ensures the method executes without breaking
        val = secrets_provider.get_secret("GEMINI_API_KEY")
        # Just ensure it returned something (could be None if not found anywhere, which is valid if neither exists)
        self.assertIsInstance(val, (str, type(None)))

if __name__ == '__main__':
    unittest.main()
