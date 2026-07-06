import asyncio
from typing import Callable, Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class EventBus:
    """
    Central Pub/Sub Event Bus.
    Includes strict retry logic, exponential backoff, and Dead Letter Queue (DLQ).
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.dead_letter_queue: List[Dict[str, Any]] = []

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logging.info(f"📡 [EventBus] Subscribed to {event_type}")

    async def publish(self, event_type: str, payload: Dict[str, Any], retries: int = 3):
        logging.info(f"📡 [EventBus] Publishing Event: {event_type}")
        if event_type not in self.subscribers:
            logging.warning(f"⚠️ [EventBus] No subscribers for {event_type}")
            return

        for callback in self.subscribers[event_type]:
            success = False
            for attempt in range(retries):
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(payload)
                    else:
                        callback(payload)
                    success = True
                    break
                except Exception as e:
                    logging.error(f"❌ [EventBus] Error in callback for {event_type} (Attempt {attempt + 1}): {e}")
                    await asyncio.sleep(0.5 * (attempt + 1)) # Exponential backoff
            
            if not success:
                logging.critical(f"☠️ [EventBus] Moving event {event_type} to Dead Letter Queue.")
                self.dead_letter_queue.append({
                    "event_type": event_type, 
                    "payload": payload,
                    "timestamp": asyncio.get_event_loop().time()
                })

event_bus = EventBus()
