from typing import List, Dict, Any
from backend.memory.manager import MemoryManager
from backend.memory.models import CognitiveMemory
from backend.memory.engines import MemoryRetriever, MemorySummarizer, MemoryEvolution

class MemoryAPI:
    """
    Exposes the 11 mandated clean API methods for the Cognitive Memory System.
    """
    def __init__(self, user_id: str = "default_user"):
        self.manager = MemoryManager(user_id=user_id)
        self.retriever = MemoryRetriever(self.manager)
        self.summarizer = MemorySummarizer(self.manager)
        self.evolution = MemoryEvolution(self.manager)

    def remember(self, memory: CognitiveMemory) -> CognitiveMemory:
        return self.manager.remember(memory)

    def retrieve(self, category: str, filters: Dict[str, Any] = None) -> List[CognitiveMemory]:
        return self.manager.retrieve(category, filters)

    def retrieve_related(self, category: str, memory_id: str) -> List[CognitiveMemory]:
        """Retrieves memories linked via the Memory Graph."""
        # Find memories that include this memory_id in related_memory_ids
        all_memories = self.manager.retrieve(category)
        return [m for m in all_memories if memory_id in getattr(m, 'related_memory_ids', [])]

    def retrieve_recent(self, category: str, limit: int = 10) -> List[CognitiveMemory]:
        return self.manager.retrieve_recent(category, limit)

    def retrieve_similar(self, category: str, keywords: List[str], limit: int = 5) -> List[CognitiveMemory]:
        return self.retriever.retrieve_similar(category, keywords, limit)

    def summarize(self, session_id: str):
        self.summarizer.summarize_conversation(session_id)

    def archive(self, category: str, memory_id: str) -> bool:
        return self.manager.archive(category, memory_id)

    def restore(self, category: str, memory_id: str) -> bool:
        return self.manager.restore(category, memory_id)

    def forget(self, category: str, memory_id: str) -> bool:
        return self.manager.delete(category, memory_id)

    def merge(self, target_id: str, source_id: str) -> bool:
        """Merge memory tags and related IDs."""
        pass # Placeholder for merge logic

    def learn(self, decision_id: str):
        self.evolution.self_reflect(decision_id)
