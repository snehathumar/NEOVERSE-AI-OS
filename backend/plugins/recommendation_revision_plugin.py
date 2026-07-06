import uuid
import json
from datetime import datetime, timezone
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus
from backend.llm_client import generate_json
from backend.analytics_service import analytics_service

REVISION_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendation_changed": {
            "type": "boolean",
            "description": "True if the new evidence forces a change in the core recommendation."
        },
        "new_recommendation": {
            "type": "string",
            "description": "The revised recommendation, if it changed."
        },
        "why_recommendation_changed": {
            "type": "string",
            "description": "Detailed reasoning for the revision."
        },
        "old_confidence": {
            "type": "integer"
        },
        "new_confidence": {
            "type": "integer"
        },
        "new_evidence": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The specific new data points from monitoring that triggered this review."
        }
    },
    "required": [
        "recommendation_changed", "new_recommendation", 
        "why_recommendation_changed", "old_confidence", 
        "new_confidence", "new_evidence"
    ]
}

class RecommendationRevisionPlugin(NeoversePlugin):
    """
    Independent engine that listens for Monitoring Alerts.
    Compares new evidence against previous decisions and revises recommendations if necessary.
    Maintains a strict revision history without ever overwriting past decisions.
    """
    def initialize(self):
        # Triggered whenever new monitoring evidence arrives
        event_bus.subscribe("MonitoringAlert", self.evaluate_new_evidence)

    def evaluate_new_evidence(self, payload: dict):
        """
        Evaluates new monitoring data against the existing decision.
        """
        # In a real system, we'd fetch the existing decision from Firestore using the user_id/context
        # For the architecture frame, we'll mock the previous state extraction
        event_description = payload.get("event_description", "")
        event_type = payload.get("event_type", "Unknown")
        
        # Mock previous state
        previous_recommendation = "Maintain current market positioning and expand slowly."
        old_confidence = 85
        
        prompt = f"""
You are the Recommendation Revision Engine.
New monitoring evidence has been detected. You must compare the Previous Recommendation with the New Situation.
If necessary, change the recommendation. Never overwrite history, we are generating a new revision entry.

Previous Recommendation: "{previous_recommendation}"
Old Confidence: {old_confidence}%

New Situation / Evidence Detected:
Event Type: {event_type}
Details: {event_description}

Decide if the recommendation should change. 
Always explain why it changed (or why it stayed the same), provide the Old Confidence, New Confidence, and list the New Evidence.
Return strictly JSON matching the schema.
"""
        try:
            result = generate_json(prompt, REVISION_SCHEMA)
            
            # Log the revision history independently
            revision_log = {
                "revision_id": str(uuid.uuid4()),
                "triggering_event_id": payload.get("log_id"),
                "recommendation_changed": result.get("recommendation_changed"),
                "new_recommendation": result.get("new_recommendation"),
                "reason": result.get("why_recommendation_changed"),
                "old_confidence": result.get("old_confidence"),
                "new_confidence": result.get("new_confidence"),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Publish revision event so analytics/memory can safely append to history
            event_bus.publish("RecommendationRevised", revision_log)
            print(f"[Revision Engine] Processed evidence. Changed? {result.get('recommendation_changed')}")
            
        except Exception as e:
            print(f"[Revision Engine] Failed to evaluate evidence: {e}")

