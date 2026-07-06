from typing import List, Dict, Any
from backend.repositories.base import BaseRepository
from backend.platform.storage.models import Decision

class DecisionRepository(BaseRepository):
    def __init__(self):
        super().__init__("decisions")

    def create_decision(self, prompt: str, facts: list, confidence: int, recommendation: str) -> Decision:
        decision = Decision(
            prompt=prompt,
            facts=facts,
            confidence=confidence,
            recommendation=recommendation
        )
        return self.storage.save_decision(decision)

    def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        decisions = self.storage.search("decisions", {})
        decisions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return decisions[:limit]
    
    def query(self) -> List[Dict[str, Any]]:
        return self.storage.search("decisions", {})
        
    def update_decision_state(self, decision_id: str, new_state: str, reviewer_info: dict, justification: str = None, confidence_score: int = None) -> bool:
        decision_data = self.storage.get("decisions", decision_id)
        if not decision_data:
            return False
            
        previous_state = decision_data.get("state", "Pending Review")
        
        # Create history entry
        from backend.platform.storage.models import ApprovalHistory
        import time
        
        history_entry = ApprovalHistory(
            previous_state=previous_state,
            new_state=new_state,
            reviewer_id=reviewer_info.get("id", "unknown"),
            reviewer_name=reviewer_info.get("name", "Unknown User"),
            reviewer_role=reviewer_info.get("role", "User"),
            justification=justification,
            confidence_score=confidence_score,
            comment=reviewer_info.get("comment")
        ).model_dump(mode='json')
        
        # Append history
        history = decision_data.get("approval_history", [])
        history.append(history_entry)
        
        # Calculate duration
        created_at_ts = decision_data.get("created_at", "")
        # Very simple duration calculation
        duration_ms = 0 # Can be calculated properly with datetime parsing
        
        updates = {
            "state": new_state,
            "reviewer_id": reviewer_info.get("id"),
            "reviewer_name": reviewer_info.get("name"),
            "reviewer_role": reviewer_info.get("role"),
            "approval_level": reviewer_info.get("approval_level", "L1"),
            "approval_source": "UI",
            "review_comments": reviewer_info.get("comment"),
            "review_duration_ms": duration_ms,
            "final_human_action": new_state,
            "approval_history": history
        }
        
        success = self.storage.update("decisions", decision_id, updates)
        
        # If successfully updated, publish events
        if success:
            try:
                # Optional: Push to event bus / learning engine
                from backend.core.event_bus import event_bus
                event_bus.publish("decision_state_changed", {
                    "decision_id": decision_id,
                    "previous_state": previous_state,
                    "new_state": new_state,
                    "reviewer": reviewer_info.get("name")
                })
            except Exception:
                pass
                
            if "Override" in new_state:
                try:
                    from backend.core.learning_engine import learning_engine
                    learning_engine.log_override({
                        "decision_id": decision_id,
                        "justification": justification,
                        "confidence_score": confidence_score
                    })
                except Exception:
                    pass
                    
        return success
