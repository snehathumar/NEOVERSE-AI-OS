from backend.model_orchestrator.dynamic_models import generate_json
from backend.memory.manager import MemoryManager
from datetime import datetime, timezone

class MindChangerEngine:
    """
    AI Changes Its Mind Engine.
    Recalculates confidence and updates recommendations based on new evidence.
    """
    def __init__(self):
        self.memory_manager = MemoryManager()
        
    async def process_new_evidence(self, decision_id: str, new_evidence: dict):
        decision = self.memory_manager.get("decision", decision_id)
        if not decision:
            return None
            
        print(f"🧠 [MindChanger] Re-evaluating decision {decision_id} based on new evidence...")
        
        schema = {
            "type": "object",
            "properties": {
                "recommendation_changed": {"type": "boolean"},
                "new_recommendation": {"type": "string"},
                "new_confidence": {"type": "integer"},
                "explanation_of_change": {"type": "string"}
            },
            "required": ["recommendation_changed", "new_recommendation", "new_confidence", "explanation_of_change"]
        }
        
        prompt = f"""
        Old Recommendation: {decision.recommendation}
        Old Confidence: {decision.confidence}
        New Evidence Arrived: {new_evidence}
        
        Does this new evidence change the recommendation? 
        If yes, provide the new recommendation, the new confidence score, and explicitly explain WHY it changed.
        """
        
        result = generate_json(prompt, schema)
        
        # Save new version to memory
        decision.recommendation = result["new_recommendation"]
        decision.confidence = result["new_confidence"]
        decision.audit_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "mind_changed",
            "explanation": result["explanation_of_change"]
        })
        
        # Increase importance since it's actively evolving
        decision.importance_score = min(decision.importance_score + 10, 100)
        decision.version += 1
        
        self.memory_manager.remember(decision)
        print(f"✅ [MindChanger] Decision updated to v{decision.version}.")
        
        return result

mind_changer = MindChangerEngine()
