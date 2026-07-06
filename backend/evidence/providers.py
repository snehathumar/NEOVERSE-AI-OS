import abc
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from backend.evidence.models import EvidenceItem, VerificationStatus, BiasReport
from backend.memory.manager import MemoryManager

class BaseResearchProvider(abc.ABC):
    """
    Interface for Research Providers.
    """
    @abc.abstractmethod
    async def search(self, query: str, context: dict) -> List[Dict[str, Any]]:
        """Returns raw evidence dictionaries."""
        pass


class InternalMemoryProvider(BaseResearchProvider):
    """
    Searches the Enterprise Memory System for historical decisions, facts, and learnings.
    """
    def __init__(self):
        self.memory_manager = MemoryManager()
        
    async def search(self, query: str, context: dict) -> List[Dict[str, Any]]:
        # Semantic search against Knowledge, Decisions, and Learnings
        results = []
        for category in ["knowledge", "decision", "learning"]:
            memories = self.memory_manager.retrieve_semantic(category, query, limit=3)
            for mem in memories:
                results.append({
                    "id": str(uuid.uuid4()),
                    "source_name": f"Internal {category.capitalize()} Memory",
                    "source_type": "internal",
                    "title": getattr(mem, "insight", getattr(mem, "original_question", "Internal Record")),
                    "content_summary": mem.model_dump_json(),
                    "author": mem.user_id,
                    "timestamp": mem.created_at,
                    "citation_metadata": {"memory_id": mem.id, "category": mem.category}
                })
        return results


class KnowledgeBaseProvider(BaseResearchProvider):
    """
    Searches uploaded Enterprise Documents and persistent Storage.
    (Mocked for now until document indexing is built)
    """
    async def search(self, query: str, context: dict) -> List[Dict[str, Any]]:
        # Placeholder for RAG against uploaded PDFs/Docs
        return []


class WebSearchProvider(BaseResearchProvider):
    """
    Searches the live web via SERP APIs or Native Tooling.
    (Interface implementation placeholder as requested by user)
    """
    async def search(self, query: str, context: dict) -> List[Dict[str, Any]]:
        # TODO: Implement real web search integration
        return []
