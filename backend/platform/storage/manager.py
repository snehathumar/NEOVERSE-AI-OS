from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.platform.storage.models import (
    User, Session, Message, Decision, Universe, Debate, Report, Event, 
    Memory, Learning, Analytics, Monitoring
)

class StorageManager(ABC):
    """
    Abstract Base Class for the Enterprise Storage Layer.
    This is the ONLY gateway to the database.
    """
    
    @abstractmethod
    def initialize(self):
        """Initialize the storage layer (e.g. connections, tables)"""
        pass

    @abstractmethod
    def save(self, collection: str, document_id: str, data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def batch_write(self, writes: List[Dict[str, Any]]) -> bool:
        pass

    @abstractmethod
    def run_transaction(self, callback) -> Any:
        pass

    @abstractmethod
    def save_user(self, user: User) -> User:
        pass

    @abstractmethod
    def save_session(self, session: Session) -> Session:
        pass

    @abstractmethod
    def save_message(self, message: Message) -> Message:
        pass

    @abstractmethod
    def save_decision(self, decision: Decision) -> Decision:
        pass

    @abstractmethod
    def save_universe(self, universe: Universe) -> Universe:
        pass

    @abstractmethod
    def save_debate(self, debate: Debate) -> Debate:
        pass

    @abstractmethod
    def save_report(self, report: Report) -> Report:
        pass

    @abstractmethod
    def save_event(self, event: Event) -> Event:
        pass

    @abstractmethod
    def save_memory(self, memory: Memory) -> Memory:
        pass

    @abstractmethod
    def save_learning(self, learning: Learning) -> Learning:
        pass

    @abstractmethod
    def save_monitoring(self, monitoring: Monitoring) -> Monitoring:
        pass

    @abstractmethod
    def save_analytics(self, analytics: Analytics) -> Analytics:
        pass

    @abstractmethod
    def get_history(self, session_id: str) -> List[Message]:
        pass

    @abstractmethod
    def search(self, collection: str, query: Dict[str, Any]) -> List[Any]:
        pass

    @abstractmethod
    def delete(self, collection: str, document_id: str) -> bool:
        pass

    @abstractmethod
    def update(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        pass
