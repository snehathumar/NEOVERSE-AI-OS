from backend.model_orchestrator.dynamic_models import generate_json
import time

class EmergencyDetectionEngine:
    """
    Detects abnormal situations (e.g. Revenue Crash) and generates Recovery Plans.
    """
    def generate_recovery_plan(self, emergency_event: dict, business_context: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "severity_assessment": {"type": "string"},
                "immediate_steps": {"type": "array", "items": {"type": "string"}},
                "recovery_plan": {"type": "array", "items": {"type": "string"}},
                "tracked_recovery_metrics": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["severity_assessment", "immediate_steps", "recovery_plan", "tracked_recovery_metrics"]
        }
        
        prompt = f"""
        EMERGENCY DETECTED: {emergency_event}
        Business Context: {business_context}
        
        Generate a strict, prioritized Recovery Plan. 
        List immediate actions to stop the bleeding, and tracked metrics to monitor recovery.
        """
        
        print(f"🚨 [Emergency Engine] Generating recovery plan for {emergency_event.get('type', 'Unknown Emergency')}")
        plan = generate_json(prompt, schema)
        plan["generated_at"] = time.time()
        return plan

emergency_engine = EmergencyDetectionEngine()
