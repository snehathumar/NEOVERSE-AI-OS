from typing import Dict, Any
import asyncio
from backend.evolution.engine import SelfEvolutionEngine
from backend.platform.cloud.logging_provider import cloud_logger

class FeedbackAPI:
    """
    Exposes a service interface for ingesting delayed real-world feedback.
    """
    def __init__(self):
        self.evolution_engine = SelfEvolutionEngine()
        
    async def submit_feedback(self, decision_id: str, feedback_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives delayed outcome feedback (e.g. ROI, Success/Failure, Comments).
        Triggers the async Feedback Learning Loop.
        """
        cloud_logger.info(f"Feedback API received feedback for {decision_id}")
        
        # Dispatch to background task to prevent blocking the API request
        asyncio.create_task(
            self.evolution_engine.process_delayed_feedback(decision_id, feedback_payload)
        )
        
        return {"status": "accepted", "message": "Feedback ingested and learning loop triggered."}
