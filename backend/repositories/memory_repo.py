from typing import List, Dict, Any
from backend.repositories.base import BaseRepository
from backend.platform.storage.models import Message

class ConversationMemoryRepository(BaseRepository):
    def __init__(self):
        super().__init__("messages")

    def add_message(self, session_id: str, role: str, content: str) -> Message:
        msg = Message(session_id=session_id, role=role, content=content)
        return self.storage.save_message(msg)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        history = self.storage.get_history(session_id)
        # Convert to dict for LLM consumption
        return [{"role": m.role, "content": m.content} for m in history]

class LearningMemoryRepository(BaseRepository):
    def __init__(self):
        super().__init__("learnings")
        
    # Methods for Learning engine can go here, using self.storage.save_learning()
