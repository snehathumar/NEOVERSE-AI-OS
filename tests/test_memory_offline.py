import os
from backend.memory.manager import MemoryManager
from backend.memory.models import ConversationMemory

def test_offline_memory_persistence():
    """
    Validates that MemoryManager successfully falls back to SQLite
    when cloud connection is disabled or unavailable.
    """
    # Force offline mode
    os.environ["USE_CLOUD_STORAGE"] = "false"
    
    manager = MemoryManager(user_id="offline_tenant_1")
    
    # Save memory
    mem = ConversationMemory(content="This is an offline test.")
    saved = manager.remember(mem)
    
    assert saved.id is not None
    
    # Retrieve it
    retrieved = manager.get("conversation", saved.id)
    assert retrieved is not None
    assert retrieved.content == "This is an offline test."
