from typing import List, Optional
from datetime import datetime, timezone
import json

from backend.platform.cloud.config import cloud_config
from backend.platform.cloud.logging_provider import cloud_logger
from backend.memory.models import CognitiveMemory, ConversationMemory, DecisionMemory, KnowledgeMemory
from backend.llm_client import GeminiClient

class MemoryLifecycleEngine:
    """
    Handles automatic memory summarization, compression, archiving, and deduplication.
    """
    def __init__(self, memory_manager):
        self.manager = memory_manager
        self.llm = GeminiClient()

    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation: 1 word ~ 1.3 tokens."""
        if not text: return 0
        return int(len(text.split()) * 1.3)

    def enforce_token_limits(self, memory: CognitiveMemory) -> CognitiveMemory:
        """Checks if a memory exceeds its respective token limit and triggers summarization."""
        if isinstance(memory, ConversationMemory):
            tokens = self._estimate_tokens(memory.content)
            if tokens > cloud_config.max_conversation_tokens and not memory.is_summary:
                return self.summarize_conversation(memory)
                
        elif isinstance(memory, DecisionMemory):
            text = f"{memory.original_question} {memory.business_context} {json.dumps(memory.debate)} {memory.recommendation}"
            tokens = self._estimate_tokens(text)
            if tokens > cloud_config.max_decision_tokens:
                return self.summarize_decision(memory)
                
        return memory

    def summarize_conversation(self, memory: ConversationMemory) -> ConversationMemory:
        """Compresses conversation while preserving critical facts and action items."""
        cloud_logger.info(f"Summarizing ConversationMemory {memory.id} to preserve tokens.")
        
        prompt = f"""
        Compress this conversation history into a dense summary.
        PRESERVE:
        - Critical facts
        - Open questions
        - Action items
        - User preferences mentioned
        
        CONVERSATION:
        {memory.content}
        
        Output format JSON:
        {{
            "summary": "...",
            "key_facts": ["..."],
            "action_items": ["..."],
            "open_questions": ["..."]
        }}
        """
        try:
            res_text = self.llm.generate(prompt)
            # basic json extraction
            import re
            json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                memory.content = data.get("summary", memory.content)
                memory.key_facts.extend(data.get("key_facts", []))
                memory.action_items.extend(data.get("action_items", []))
                memory.open_questions.extend(data.get("open_questions", []))
                memory.is_summary = True
                
                # Increment version
                memory.version += 1
                memory.audit_history.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "summarized",
                    "reason": "token limit exceeded"
                })
        except Exception as e:
            cloud_logger.error(f"Failed to summarize conversation {memory.id}: {e}")
            
        return memory

    def summarize_decision(self, memory: DecisionMemory) -> DecisionMemory:
        """Compresses decision memory by simplifying debate and universe arrays."""
        cloud_logger.info(f"Compressing DecisionMemory {memory.id}.")
        # We strip the dense debate dict into a summary string
        if memory.debate:
            memory.debate = {"compressed_summary": "Debate occurred. See previous versions or logs for full transcript."}
        
        if len(memory.universes) > 3:
            memory.universes = memory.universes[:3] # keep only top 3 universes
            
        memory.version += 1
        memory.audit_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "compressed",
            "reason": "decision token limit exceeded"
        })
        return memory

    def merge_knowledge(self, new_insight: KnowledgeMemory, domain: str) -> Optional[KnowledgeMemory]:
        """
        Deduplicates Knowledge. If similar knowledge exists, it merges them to prevent fragmentation.
        Returns the merged memory if merged, None if it should be saved as new.
        """
        existing = self.manager.retrieval_engine.semantic_search("knowledge", new_insight.insight, limit=3, filters={"domain": domain})
        if not existing:
            return None
            
        top_match = existing[0]
        # Very rough threshold - in production this would be cosine similarity > 0.85
        if top_match.importance_score > 40:
            cloud_logger.info(f"Merging new insight into existing KnowledgeMemory {top_match.id}")
            prompt = f"""
            Merge these two insights into a single comprehensive fact.
            Insight 1: {top_match.insight}
            Insight 2: {new_insight.insight}
            """
            merged_text = self.llm.generate(prompt).strip()
            
            top_match.insight = merged_text
            top_match.importance_score += 10 # Increase importance for being corroborated
            if new_insight.source_document and new_insight.source_document not in top_match.references:
                top_match.references.append(new_insight.source_document)
                
            top_match.version += 1
            top_match.audit_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "merged",
                "merged_with": new_insight.id
            })
            
            return self.manager.remember(top_match)
            
        return None
