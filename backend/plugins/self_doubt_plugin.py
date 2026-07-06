import json
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus
from backend.llm_client import generate_json
from backend.analytics_service import analytics_service

SELF_DOUBT_SCHEMA = {
    "type": "object",
    "properties": {
        "possible_hallucinations": {
            "type": "array",
            "items": {"type": "string"}
        },
        "weak_assumptions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "missing_evidence": {
            "type": "array",
            "items": {"type": "string"}
        },
        "high_uncertainty": {
            "type": "array",
            "items": {"type": "string"}
        },
        "unknown_factors": {
            "type": "array",
            "items": {"type": "string"}
        },
        "confidence_before": {
            "type": "integer"
        },
        "confidence_after": {
            "type": "integer",
            "description": "Must be lower than confidence_before if uncertainty is found."
        },
        "reasons": {
            "type": "string",
            "description": "Detailed explanation of why the confidence was reduced."
        }
    },
    "required": [
        "possible_hallucinations", 
        "weak_assumptions", 
        "missing_evidence", 
        "high_uncertainty", 
        "unknown_factors", 
        "confidence_before", 
        "confidence_after", 
        "reasons"
    ]
}

class SelfDoubtPlugin(NeoversePlugin):
    """
    Independent Self-Doubt Engine.
    Evaluates AI recommendations to ensure confidence is never artificially inflated.
    """
    def initialize(self):
        # Subscribes to the event bus. It evaluates EVERY decision made by the system.
        event_bus.subscribe("DecisionCreated", self.evaluate_recommendation)

    def evaluate_recommendation(self, payload: dict):
        """
        Triggered asynchronously whenever a decision is completed.
        Analyzes the payload, calculates doubt, and logs it.
        """
        decision_query = payload.get("decision_query", "")
        recommendation = payload.get("final_recommendation", "")
        confidence = payload.get("confidence_score", 100)
        
        prompt = f"""
You are the Self-Doubt Engine.
Evaluate the following AI recommendation.
Identify:
1. Possible hallucinations
2. Weak assumptions
3. Missing evidence
4. High uncertainty
5. Unknown factors

Instead of increasing confidence, you MUST reduce confidence whenever uncertainty increases.
Original Decision Query: "{decision_query}"
AI Recommendation: "{recommendation}"
Confidence Before: {confidence}

Return strictly JSON matching the schema.
"""
        # In a real run, this calls the LLM. 
        # For safety/architecture framing, we wrap the call.
        try:
            result = generate_json(prompt, SELF_DOUBT_SCHEMA)
            
            # Fire an event if confidence was significantly reduced
            if result.get("confidence_after", 100) < confidence:
                event_bus.publish("ConfidenceUpdated", {
                    "decision_id": payload.get("decision_id"),
                    "confidence_before": confidence,
                    "confidence_after": result.get("confidence_after"),
                    "reasons": result.get("reasons")
                })
        except Exception as e:
            print(f"[SelfDoubtPlugin] Failed to evaluate recommendation: {e}")

# Note: Because of PluginManager, we don't need to explicitly instantiate this globally here.
