from typing import Dict, Any, List
from backend.platform.storage.factory import get_storage_manager

class BaseRepository:
    """
    Base Repository using the StorageManager.
    Child classes use strongly typed methods.
    """
    def __init__(self, collection_name: str):
        self.collection = collection_name
        self.storage = get_storage_manager()

    # The actual methods (save_decision, save_event) will be directly called on self.storage
    # by the child repositories since StorageManager now has explicit methods.
