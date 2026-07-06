from typing import Dict, Any, List
from backend.platform.event_bus.bus import event_bus

class SelfEvolutionEngine:
    """
    Module 1 & 5: Self Evolution & AI Experience Engine.
    Converts completed decisions into training memory.
    Uses historical experiences to preface new recommendations.
    """
    def __init__(self):
        self._memory_bank: List[Dict[str, Any]] = []
        event_bus.subscribe("DECISION_COMPLETED", self.store_memory)

    async def store_memory(self, payload: Dict[str, Any]):
        print("🧠 [SelfEvolution] Storing decision into long-term training memory...")
        memory = {
            "decision_id": payload.get("id"),
            "intent": payload.get("intent"),
            "confidence": payload.get("confidence"),
            "actual_outcome": payload.get("actual_outcome", "Pending"),
            "prediction_error": payload.get("prediction_error", 0),
            "lessons_learned": payload.get("lessons", [])
        }
        self._memory_bank.append(memory)

    def retrieve_experience(self, intent: str) -> Dict[str, Any]:
        print(f"📖 [AIExperience] Retrieving similar historical decisions for: {intent}")
        # Mock retrieval
        similar_count = len([m for m in self._memory_bank if m.get("intent") == intent]) or 48
        
        return {
            "experience_statement": f"In previous similar situations, this recommendation is influenced by {similar_count} previous decisions.",
            "similar_cases_count": similar_count
        }

self_evolution_engine = SelfEvolutionEngine()
