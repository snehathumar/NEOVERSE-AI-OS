import json
import uuid
from datetime import datetime, timezone
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus
from backend.llm_client import generate_json

EMERGENCY_SCHEMA = {
    "type": "object",
    "properties": {
        "is_emergency": {
            "type": "boolean",
            "description": "True if the situation constitutes a severe emergency (e.g. Revenue Drop, Cash Flow Crisis)."
        },
        "severity": {
            "type": "string",
            "enum": ["Low", "Medium", "High", "Critical"],
            "description": "The severity level of the emergency."
        },
        "emergency_report": {
            "type": "string",
            "description": "A concise report detailing the crisis."
        },
        "recovery_strategy": {
            "type": "string",
            "description": "High-level strategic pivot to survive the emergency."
        },
        "priority_actions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Immediate steps to execute today to mitigate damage."
        },
        "confidence": {
            "type": "integer",
            "description": "Confidence (0-100) in the proposed recovery strategy."
        }
    },
    "required": [
        "is_emergency", "severity", "emergency_report", 
        "recovery_strategy", "priority_actions", "confidence"
    ]
}

class EmergencyPlugin(NeoversePlugin):
    """
    Emergency Engine.
    Detects critical business situations (Revenue Drop, Customer Loss, Cash Flow Crisis, 
    Inventory Failure, Supplier Risk) and automatically generates recovery strategies.
    """
    def initialize(self):
        # Listens to monitoring alerts to detect if a background event escalated into an emergency
        event_bus.subscribe("MonitoringAlert", self.evaluate_for_emergency)
        
    def evaluate_for_emergency(self, payload: dict):
        """
        Evaluates a monitoring alert or business state update to see if it triggers an emergency protocol.
        """
        event_description = payload.get("event_description", "")
        event_type = payload.get("event_type", "Unknown")
        
        prompt = f"""
You are the Emergency Engine.
Your job is to detect if the following business event constitutes a severe emergency.
Look for: Revenue Drop, Customer Loss, Cash Flow Crisis, Inventory Failure, or Supplier Risk.

Event Type: {event_type}
Event Details: "{event_description}"

If it is an emergency, set 'is_emergency' to true and generate an Emergency Report, Severity, Recovery Strategy, and Priority Actions.
If it is NOT an emergency, set 'is_emergency' to false and provide placeholder values.

Return strictly JSON matching the schema.
"""
        try:
            result = generate_json(prompt, EMERGENCY_SCHEMA)
            
            if result.get("is_emergency"):
                print(f"🚨 [EMERGENCY PROTOCOL ACTIVATED] Severity: {result.get('severity')}")
                # Publish the emergency so other systems (like UI alerts or CEO dashboards) can react
                result["trigger_event"] = event_description
                result["timestamp"] = datetime.now(timezone.utc).isoformat()
                event_bus.publish("EmergencyProtocolActivated", result)
                
        except Exception as e:
            print(f"[Emergency Engine] Failed to evaluate event: {e}")

    def analyze_manual_crisis(self, crisis_description: str) -> dict:
        """
        Allows direct injection of a crisis (e.g. from the user directly via chat).
        """
        prompt = f"""
You are the Emergency Engine.
The user has reported a severe business crisis: "{crisis_description}"
Assume this is a genuine emergency.
Generate an Emergency Report, determine Severity, provide a Recovery Strategy, and list Priority Actions.

Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, EMERGENCY_SCHEMA)
        except Exception as e:
            return {"is_emergency": True, "severity": "Unknown", "emergency_report": str(e), "recovery_strategy": "", "priority_actions": [], "confidence": 0}

