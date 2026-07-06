from typing import Dict, Any
from backend.platform.event_bus.bus import event_bus

class AutonomousUpdateTrigger:
    """
    Module 3: Autonomous Recommendation Update.
    Monitors external evidence changes and triggers reevaluation.
    """
    def __init__(self):
        event_bus.subscribe("EVIDENCE_UPDATED", self.check_reevaluation)

    async def check_reevaluation(self, payload: Dict[str, Any]):
        evidence = payload.get("new_evidence", {})
        if evidence.get("impact") == "HIGH":
            print(f"🔄 [AutonomousUpdate] High impact evidence detected ({evidence.get('type')}). Triggering reevaluation...")
            # Trigger orchestrator to rethink
            await event_bus.publish("DECISION_REQUESTED", {"intent": "Reevaluate past decision", "trigger": evidence})

autonomous_update_trigger = AutonomousUpdateTrigger()
