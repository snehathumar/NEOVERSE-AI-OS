from typing import Dict, Any, List
from backend.platform.event_bus.bus import event_bus

class RecommendationVersioningEngine:
    """
    Module 6: Recommendation Versioning.
    Tracks v1, v2, v3 of a recommendation as confidence and evidence evolve.
    """
    def __init__(self):
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        event_bus.subscribe("CONFIDENCE_CHANGED", self.evaluate_version_bump)

    async def evaluate_version_bump(self, payload: Dict[str, Any]):
        decision_id = payload.get("decision_id")
        latest_conf = payload.get("latest", {}).get("confidence_score", 0)
        
        if decision_id not in self._versions:
            self._versions[decision_id] = []
            
        current_version_count = len(self._versions[decision_id])
        
        # Simple threshold bump rule
        if current_version_count == 0 or abs(self._versions[decision_id][-1]["confidence"] - latest_conf) > 5:
            new_v = {
                "version": f"v{current_version_count + 1}",
                "confidence": latest_conf,
                "strategy": payload.get("strategy", "Strategy updated based on new confidence.")
            }
            self._versions[decision_id].append(new_v)
            print(f"🏷️ [VersioningEngine] {decision_id} bumped to {new_v['version']}")

    def get_versions(self, decision_id: str) -> List[Dict[str, Any]]:
        return self._versions.get(decision_id, [])

recommendation_versioning_engine = RecommendationVersioningEngine()
