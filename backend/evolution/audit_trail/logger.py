from typing import Dict, Any
from backend.platform.event_bus.bus import event_bus
import datetime
import json

class EnterpriseAuditTrail:
    """
    Module 13: Enterprise Audit Trail.
    Logs every AI action, intent, tool usage, model usage, and decision.
    """
    def __init__(self):
        self._audit_log = []
        # Subscribe to all major events
        event_bus.subscribe("DECISION_REQUESTED", self.log_action)
        event_bus.subscribe("RECOMMENDATION_GENERATED", self.log_action)
        event_bus.subscribe("CONFIDENCE_CHANGED", self.log_action)

    async def log_action(self, payload: Dict[str, Any]):
        action_log = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event_type": payload.get("event_type", "UNKNOWN_EVENT"),
            "intent": payload.get("intent", "N/A"),
            "tools_used": payload.get("tools_used", []),
            "models_used": payload.get("models_used", ["gemini-pro"]),
            "confidence": payload.get("confidence", 0),
            "reasoning": payload.get("reasoning", "")
        }
        print(f"🔒 [AuditTrail] Action logged: {action_log['event_type']}")
        self._audit_log.append(action_log)

    def export_audit_history(self) -> str:
        return json.dumps(self._audit_log, indent=4)

enterprise_audit_trail = EnterpriseAuditTrail()
