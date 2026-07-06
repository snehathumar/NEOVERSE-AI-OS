import re
from typing import List, Dict, Any
from datetime import datetime, timezone

from backend.memory.models import CognitiveMemory
from backend.platform.cloud.logging_provider import cloud_logger

class MemoryRetrievalEngine:
    """
    Intelligent Retrieval Engine for Cognitive Memory.
    Provides scalable interfaces that can be backed by Vector Stores in the future.
    """
    def __init__(self, memory_manager):
        # We hold a reference to MemoryManager to query raw data if needed
        self.manager = memory_manager

    def extract_keywords(self, text: str) -> set:
        """Lightweight Python keyword extraction (no NLTK dependency)."""
        if not text:
            return set()
        
        # Lowercase, remove non-alphanumeric, split
        words = re.findall(r'\b[a-z0-9_]{3,}\b', text.lower())
        
        # Basic stopword list
        stopwords = {
            "the", "and", "that", "this", "with", "from", "for", "are", "have", "not",
            "you", "what", "can", "will", "would", "could", "should", "your", "our",
            "their", "there", "then", "than", "but", "also", "has", "had", "been", "was"
        }
        
        return set(w for w in words if w not in stopwords)

    def calculate_importance_score(self, memory: CognitiveMemory, current_time: datetime = None) -> float:
        """
        Combines intrinsic importance, business impact, retrieval frequency, and recency decay.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        base_importance = memory.importance_score
        business_impact = getattr(memory, 'business_impact', 50)
        freq = getattr(memory, 'retrieval_frequency', 0)
        
        # Max out frequency bonus at +20
        freq_bonus = min(freq * 2, 20)
        
        # Recency decay
        decay = 0.0
        if memory.created_at:
            try:
                created_dt = datetime.fromisoformat(memory.created_at.replace("Z", "+00:00"))
                days_old = (current_time - created_dt).days
                # Decay by 1 point per 7 days, max -30
                decay = min(days_old / 7.0, 30)
            except Exception:
                pass
                
        final_score = (base_importance * 0.4) + (business_impact * 0.4) + freq_bonus - decay
        return max(min(final_score, 100), 0)

    def semantic_search(self, category: str, query: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[CognitiveMemory]:
        """
        Placeholder for Vector DB semantic search.
        Currently uses lightweight keyword matching against tags and content-derived metadata.
        """
        query_keywords = self.extract_keywords(query)
        
        # Retrieve base set matching filters (tenant isolated by MemoryManager)
        candidates = self.manager.retrieve(category, filters)
        
        scored_candidates = []
        for memory in candidates:
            # Score based on tag overlap
            tags_set = set([t.lower() for t in memory.tags])
            overlap = len(query_keywords.intersection(tags_set))
            
            # Simple content overlap for Conversation / Decision if available
            content = ""
            if hasattr(memory, 'content'): content = memory.content
            elif hasattr(memory, 'original_question'): content = memory.original_question
            elif hasattr(memory, 'insight'): content = memory.insight
            
            content_keywords = self.extract_keywords(content)
            overlap += len(query_keywords.intersection(content_keywords)) * 0.5
            
            # If no keywords match and query wasn't empty, we penalize it
            match_score = overlap
            if query_keywords and overlap == 0:
                continue # Skip completely irrelevant memories to mimic vector threshold
                
            dynamic_importance = self.calculate_importance_score(memory)
            
            # Combine match relevance with intrinsic memory value
            total_score = (match_score * 20) + (dynamic_importance * 0.5)
            scored_candidates.append((total_score, memory))
            
        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        return [mem for score, mem in scored_candidates[:limit]]
