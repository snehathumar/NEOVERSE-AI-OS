from backend.memory.manager import MemoryManager
from backend.memory.models import CognitiveMemory
from typing import List, Dict, Any

class MemoryIndexer:
    @staticmethod
    def index_memory(memory: CognitiveMemory):
        """Computes priority, tags, and placeholder embeddings."""
        if not memory.tags:
            # Simple keyword extraction placeholder
            memory.tags = ["auto-indexed"]
        
        # Priority mapping placeholder
        if memory.confidence > 80:
            memory.priority = "high"
            memory.importance_score = min(100, memory.importance_score + 10)

class MemoryRetriever:
    def __init__(self, manager: MemoryManager):
        self.manager = manager

    def retrieve_similar(self, category: str, keywords: List[str], limit: int = 5) -> List[CognitiveMemory]:
        """Mock semantic retrieval (VectorStore placeholder)"""
        results = self.manager.retrieve(category)
        
        # Simple local scoring based on keyword overlap in tags/metadata
        def score(m):
            return sum(1 for kw in keywords if kw in m.tags or kw in str(m.model_dump()))
            
        results.sort(key=score, reverse=True)
        return results[:limit]

class MemorySummarizer:
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        
    def summarize_conversation(self, session_id: str):
        """Consolidates long conversations."""
        convos = self.manager.retrieve("conversation", {"session_id": session_id})
        if len(convos) > 20:
            # Archive old ones
            for c in convos[:-10]:
                self.manager.archive("conversation", c.id)

class MemoryEvolution:
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        
    def self_reflect(self, decision_id: str):
        """Self-evolution after a decision."""
        from backend.memory.models import LearningMemory
        learning = LearningMemory(
            lessons_learned=["Always verify assumptions"],
            prediction_errors=["Underestimated latency"],
            confidence_changes={"market_analysis": -5},
            related_memory_ids=[decision_id]
        )
        self.manager.remember(learning)

class MemoryAnalytics:
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        
    def generate_stats(self) -> Dict[str, Any]:
        convos = len(self.manager.retrieve("conversation"))
        decisions = len(self.manager.retrieve("decision"))
        learnings = len(self.manager.retrieve("learning"))
        return {
            "conversation_count": convos,
            "decision_count": decisions,
            "learning_count": learnings
        }
