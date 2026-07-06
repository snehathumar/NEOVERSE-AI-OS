import threading
from collections import defaultdict
import datetime

class EventBus:
    """
    Central Event Bus for NEOVERSE AI OS.
    Implements a robust Pub/Sub pattern to decouple all system modules.
    """
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()
        
    def subscribe(self, event_type: str, callback: callable):
        """
        Registers a callback function to listen for specific event types.
        """
        with self._lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                
    def unsubscribe(self, event_type: str, callback: callable):
        """
        Removes a callback from the event's subscriber list.
        """
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                
    def publish(self, event_type: str, payload: dict):
        """
        Broadcasts an event asynchronously to all registered subscribers.
        """
        # Ensure timestamp is attached to every event for tracing
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
        with self._lock:
            subscribers = list(self._subscribers[event_type])
            
        # Execute callbacks in separate threads to avoid blocking the publisher
        for callback in subscribers:
            threading.Thread(target=self._execute_callback, args=(callback, event_type, payload), daemon=True).start()
            
    def _execute_callback(self, callback, event_type, payload):
        try:
            callback(payload)
        except Exception as e:
            print(f"[EVENT BUS ERROR] Failed to process event '{event_type}': {e}")

# Global singleton event bus
event_bus = EventBus()
