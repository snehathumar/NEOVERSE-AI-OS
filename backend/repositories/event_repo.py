from typing import List, Dict, Any
from backend.repositories.base import BaseRepository
from backend.platform.storage.models import Event

class EventRepository(BaseRepository):
    def __init__(self):
        super().__init__("events")

    def log_event(self, event_type: str, message: str, metadata: dict = None) -> Event:
        event = Event(
            event_type=event_type,
            message=message
        )
        if metadata:
            event.metadata = metadata
        return self.storage.save_event(event)

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        events = self.storage.search("events", {})
        events.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        # Using dict dump for UI compatibility
        return [{"timestamp": e.get("created_at"), "event_type": e.get("event_type"), "message": e.get("message")} for e in events[:limit]]

    def query(self) -> List[Dict[str, Any]]:
        return self.storage.search("events", {})
