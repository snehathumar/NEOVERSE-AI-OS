import unittest
from unittest.mock import patch, MagicMock
import os

from backend.platform.cloud.secrets_provider import SecretsProvider
from backend.platform.cloud.gcs_provider import GCSProvider
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.storage.factory import FallbackStorageManager
from backend.platform.storage.sqlite_provider import SQLiteStorage

class TestCloudProvidersGracefulFallback(unittest.TestCase):
    def setUp(self):
        # Ensure fallback local dirs are clean
        self.local_gcs_dir = os.path.join(os.getcwd(), "data", "storage_fallback")
        self.local_bq_dir = os.path.join(os.getcwd(), "data", "bq_fallback")
        os.makedirs(self.local_gcs_dir, exist_ok=True)
        os.makedirs(self.local_bq_dir, exist_ok=True)
        
        # We explicitly simulate an environment where cloud libraries might exist,
        # but credentials fail or network fails, leading to exceptions.

    def test_secrets_fallback_to_env(self):
        # Force the client to throw an exception on access
        mock_client = MagicMock()
        mock_client.access_secret_version.side_effect = Exception("Cloud offline")
        
        provider = SecretsProvider(project_id="test-project")
        provider.client = mock_client
        
        os.environ["TEST_SECRET"] = "local_env_value"
        val = provider.get_secret("TEST_SECRET")
        self.assertEqual(val, "local_env_value")

    def test_gcs_fallback_to_local(self):
        # Provider with NO client (simulating no auth or offline)
        provider = GCSProvider(project_id="test-project")
        provider.client = None
        provider.bucket = None
        
        success = provider.upload_string("test_file.txt", "hello world")
        self.assertTrue(success)
        
        val = provider.download_string("test_file.txt")
        self.assertEqual(val, "hello world")
        
        # Verify it went to disk
        local_path = os.path.join(self.local_gcs_dir, "test_file.txt")
        self.assertTrue(os.path.exists(local_path))

    def test_bigquery_fallback_to_local(self):
        provider = BigQueryProvider(project_id="test-project")
        provider.client = None
        
        rows = [{"user": "test", "action": "login"}]
        success = provider.insert_rows("audit_logs", rows)
        self.assertTrue(success)
        
        local_path = os.path.join(self.local_bq_dir, "audit_logs.jsonl")
        self.assertTrue(os.path.exists(local_path))

    def test_storage_manager_fallback(self):
        # Create a mock firestore provider that always throws exceptions
        class BrokenCloudProvider:
            def save(self, *args): raise Exception("Network down")
            def get(self, *args): raise Exception("Network down")
            def update(self, *args): raise Exception("Network down")
            def delete(self, *args): raise Exception("Network down")
            def query(self, *args): raise Exception("Network down")

        local_sqlite = SQLiteStorage(":memory:")
        fallback_manager = FallbackStorageManager(BrokenCloudProvider(), local_sqlite)
        
        # Even though cloud is broken, save should succeed via SQLite
        doc_id = fallback_manager.save("users", "user1", {"name": "Test"})
        self.assertEqual(doc_id, "user1")
        
        # Get should also succeed
        doc = fallback_manager.get("users", "user1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["name"], "Test")

if __name__ == '__main__':
    unittest.main()
