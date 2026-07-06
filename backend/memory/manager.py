from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from backend.platform.storage.factory import get_storage_manager
from backend.memory.models import CognitiveMemory
from backend.memory.retrieval import MemoryRetrievalEngine
from backend.memory.lifecycle import MemoryLifecycleEngine
from backend.platform.cloud.logging_provider import cloud_logger

class MemoryManager:
    """
    Central API for the Enterprise Cognitive Memory System.
    Strictly uses StorageManager for all persistence operations.
    Multi-tenant by default.
    """
    def __init__(self, user_id: str = "default_user", org_id: str = "default_org"):
        self.user_id = user_id
        self.org_id = org_id
        self.storage = get_storage_manager()
        self.retrieval_engine = MemoryRetrievalEngine(self)
        self.lifecycle_engine = MemoryLifecycleEngine(self)

    def _get_model_class(self, category: str):
        from backend.memory.models import (
            ConversationMemory, DecisionMemory, LearningMemory, KnowledgeMemory,
            MonitoringMemory, UserProfileMemory, SessionMemory, AgentStateMemory, 
            CognitiveMemory, DigitalTwinMemory
        )
        mapping = {
            "conversation": ConversationMemory,
            "decision": DecisionMemory,
            "learning": LearningMemory,
            "knowledge": KnowledgeMemory,
            "monitoring": MonitoringMemory,
            "user_profile": UserProfileMemory,
            "session": SessionMemory,
            "agent_state": AgentStateMemory,
            "digital_twin": DigitalTwinMemory
        }
        return mapping.get(category, CognitiveMemory)

    def remember(self, memory: CognitiveMemory) -> CognitiveMemory:
        """Saves a new memory to the persistent store."""
        memory.user_id = self.user_id
        
        # Enforce multi-tenancy at the memory level if supported by model, 
        # or we just enforce it at the collection level.
        if hasattr(memory, 'org_id'):
            memory.org_id = self.org_id
        
        # 1. Enforce Lifecycle token limits
        memory = self.lifecycle_engine.enforce_token_limits(memory)
        
        # 2. Knowledge Deduplication
        if memory.category == "knowledge":
            from backend.memory.models import KnowledgeMemory
            if isinstance(memory, KnowledgeMemory):
                merged = self.lifecycle_engine.merge_knowledge(memory, memory.domain)
                if merged:
                    return merged # it was merged and saved

        collection = f"org_{self.org_id}_{memory.category}s"
        
        # StorageManager takes dict payloads
        self.storage.save(collection, memory.id, memory.model_dump())
        return memory

    def get(self, category: str, memory_id: str) -> Optional[CognitiveMemory]:
        """Retrieve a specific memory by its ID."""
        collection = f"org_{self.org_id}_{category}s"
        raw = self.storage.get(collection, memory_id)
        if not raw:
            return None
            
        model_class = self._get_model_class(category)
        try:
            mem = model_class(**raw)
            self._update_access_metrics(collection, mem)
            return mem
        except Exception as e:
            cloud_logger.error(f"Failed to deserialize memory {memory_id}: {e}")
            return None

    def retrieve(self, category: str, filters: Dict[str, Any] = None) -> List[CognitiveMemory]:
        """Base retrieval function enforcing user isolation."""
        collection = f"org_{self.org_id}_{category}s"
        f = {"user_id": self.user_id, "lifecycle_state": "active"}
        if filters:
            f.update(filters)
        
        model_class = self._get_model_class(category)
        
        # Storage search returns dicts, we need to deserialize
        raw_results = self.storage.search(collection, f)
        
        results = []
        for raw in raw_results:
            try:
                mem = model_class(**raw)
                results.append(mem)
                
                # Active Score Updating
                self._update_access_metrics(collection, mem)
            except Exception as e:
                cloud_logger.error(f"Failed to deserialize memory {raw.get('id')}: {e}")
                
        return results

    def _update_access_metrics(self, collection: str, memory: CognitiveMemory):
        """Asynchronously updates frequency and last access time."""
        memory.retrieval_frequency += 1
        memory.last_access_time = datetime.now(timezone.utc).isoformat()
        # In a high-traffic env, we'd batch this or use Firestore increment
        # Here we do a lightweight update to avoid rewriting the whole document
        try:
            self.storage.save(collection, memory.id, {
                "retrieval_frequency": memory.retrieval_frequency,
                "last_access_time": memory.last_access_time
            })
        except Exception:
            pass

    def retrieve_semantic(self, category: str, query: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[CognitiveMemory]:
        """Intelligent semantic retrieval via keyword/vector placeholder."""
        start_time = datetime.now()
        results = self.retrieval_engine.semantic_search(category, query, limit, filters)
        latency = (datetime.now() - start_time).total_seconds()
        
        # Stream analytics
        try:
            from backend.analytics.memory_analytics import memory_analytics
            memory_analytics.record_retrieval(self.user_id, category, latency, len(results))
        except Exception:
            pass
            
        return results

    def retrieve_recent(self, category: str, limit: int = 10) -> List[CognitiveMemory]:
        results = self.retrieve(category)
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results[:limit]

    def archive(self, category: str, memory_id: str) -> bool:
        collection = f"org_{self.org_id}_{category}s"
        try:
            self.storage.save(collection, memory_id, {"lifecycle_state": "archived"})
            return True
        except Exception:
            return False

    def delete(self, category: str, memory_id: str) -> bool:
        """Soft delete."""
        collection = f"org_{self.org_id}_{category}s"
        try:
            self.storage.save(collection, memory_id, {"lifecycle_state": "deleted"})
            return True
        except Exception:
            return False
            
    def get_agent_state(self, current_task: str) -> Optional[CognitiveMemory]:
        states = self.retrieve("agent_state", {"current_task": current_task})
        if states:
            states.sort(key=lambda x: x.created_at, reverse=True)
            return states[0]
        return None

    def get_digital_twin(self) -> Optional[CognitiveMemory]:
        twins = self.retrieve("digital_twin")
        if twins:
            twins.sort(key=lambda x: x.created_at, reverse=True)
            return twins[0]
        return None
        
    def save_digital_twin(self, twin_memory: CognitiveMemory) -> CognitiveMemory:
        return self.remember(twin_memory)
