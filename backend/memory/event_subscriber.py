from backend.platform.event_bus.bus import event_bus
from backend.memory.api import MemoryAPI
from backend.memory.models import ConversationMemory, DecisionMemory, MonitoringMemory
import logging

class MemoryEventSubscriber:
    """
    Subscribes to EventBus and automatically persists memories.
    This replaces hardcoded memory saves across the codebase.
    """
    def __init__(self, memory_api: MemoryAPI):
        self.api = memory_api
        
    def setup_subscriptions(self):
        event_bus.subscribe("USER_MESSAGE", self.handle_user_message)
        event_bus.subscribe("DECISION_CREATED", self.handle_decision)
        event_bus.subscribe("MONITORING_ALERT", self.handle_monitoring)
        event_bus.subscribe("REPORT_GENERATED", self.handle_report)
        logging.info("🧠 [MemorySystem] Subscribed to EventBus")

    def handle_user_message(self, payload: dict):
        mem = ConversationMemory(
            session_id=payload.get("session_id"),
            user_id=payload.get("user_id", "default_user"),
            role=payload.get("role", "user"),
            content=payload.get("content", ""),
            importance_score=payload.get("importance", 50)
        )
        self.api.remember(mem)
        # Trigger summarization if needed
        self.api.summarize(mem.session_id)

    def handle_decision(self, payload: dict):
        mem = DecisionMemory(
            user_id=payload.get("user_id", "default_user"),
            session_id=payload.get("session_id"),
            original_question=payload.get("prompt", ""),
            business_context=payload.get("business_context", ""),
            recommendation=payload.get("recommendation", ""),
            confidence=payload.get("confidence", 50),
            importance_score=payload.get("importance", 80)
        )
        saved = self.api.remember(mem)
        
        # Trigger self-evolution after decision
        self.api.learn(saved.id)

    def handle_monitoring(self, payload: dict):
        mem = MonitoringMemory(
            event_name=payload.get("event", "unknown_alert"),
            is_failure=payload.get("is_failure", True),
            alert_details=payload.get("details", "")
        )
        self.api.remember(mem)

    def handle_report(self, payload: dict):
        # We can store ReportMemory, linking it to the Decision via related_memory_ids
        pass

def initialize_memory_subscribers(memory_api: MemoryAPI):
    subscriber = MemoryEventSubscriber(memory_api)
    subscriber.setup_subscriptions()
