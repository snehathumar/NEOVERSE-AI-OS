from typing import Dict, Any, List
from backend.platform.event_bus.bus import event_bus

class AdaptiveConfidenceEngine:
    """
    Module 2: Adaptive Confidence Engine.
    Confidence changes over time based on new evidence, debate, and simulations.
    Tracks the evolution timeline.
    """
    def __init__(self):
        self._confidence_timeline: Dict[str, List[Dict[str, Any]]] = {}
        event_bus.subscribe("EVIDENCE_UPDATED", self.recalculate_confidence)

    async def recalculate_confidence(self, payload: Dict[str, Any]):
        decision_id = payload.get("decision_id", "Unknown")
        if decision_id not in self._confidence_timeline:
            self._confidence_timeline[decision_id] = []
            
        stage = payload.get("stage", "Initial")
        new_score = payload.get("calculated_score", 60)
        
        entry = {
            "stage": stage,
            "confidence_score": new_score,
            "reason": payload.get("reason", "Base calculation")
        }
        self._confidence_timeline[decision_id].append(entry)
        
        print(f"📈 [AdaptiveConfidence] {decision_id} updated -> {new_score}% ({stage})")
        await event_bus.publish("CONFIDENCE_CHANGED", {"decision_id": decision_id, "latest": entry})

    def get_timeline(self, decision_id: str) -> List[Dict[str, Any]]:
        return self._confidence_timeline.get(decision_id, [])

adaptive_confidence_engine = AdaptiveConfidenceEngine()
