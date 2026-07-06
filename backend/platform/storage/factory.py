import os
from typing import Dict, Any, List, Optional
from backend.platform.storage.manager import StorageManager
from backend.platform.storage.sqlite_provider import SQLiteStorage
from backend.platform.cloud.logging_provider import cloud_logger

class FallbackStorageManager:
    """
    Wraps Firestore and SQLite dynamically. Attempts cloud method first, 
    and gracefully falls back to local if there's a transient cloud failure or missing implementation.
    """
    def __init__(self, cloud_provider, local_provider):
        self.cloud = cloud_provider
        self.local = local_provider

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            if self.cloud and hasattr(self.cloud, name):
                try:
                    cloud_method = getattr(self.cloud, name)
                    return cloud_method(*args, **kwargs)
                except Exception as e:
                    cloud_logger.error(f"Cloud {name} failed: {e}. Falling back to local.")
            
            # Local fallback
            if hasattr(self.local, name):
                local_method = getattr(self.local, name)
                return local_method(*args, **kwargs)
            else:
                raise AttributeError(f"Method {name} not implemented in cloud or local provider.")
                
        return wrapper

_instance = None

def get_storage_manager() -> StorageManager:
    """
    Factory function returning a FallbackStorageManager.
    """
    global _instance
    if _instance is not None:
        return _instance

    use_cloud = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    local_provider = SQLiteStorage()
    cloud_provider = None

    if use_cloud or gcp_creds:
        try:
            from backend.platform.storage.firestore_provider import FirestoreProvider
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
            cloud_provider = FirestoreProvider(project_id=project_id)
            cloud_logger.info("Firestore initialized successfully.")
        except Exception as e:
            cloud_logger.warning(f"Failed to initialize Firestore: {e}. Running in Local-Only mode.")
            
    _instance = FallbackStorageManager(cloud_provider, local_provider)
    return _instance
