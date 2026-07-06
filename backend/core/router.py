from backend.model_orchestrator.dynamic_models import generate_json
from backend.core.intent_models import IntentType
from backend.core.intent_handlers import intent_handlers
import json

class MasterRouter:
    """
    The Master AI Router.
    Classifies every request to ensure the heavy Decision Pipeline is only activated when necessary.
    """
    def classify_intent(self, user_input: str) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [e.value for e in IntentType]
                },
                "confidence": {"type": "number"},
                "explanation": {"type": "string"}
            },
            "required": ["intent", "confidence", "explanation"]
        }
        
        prompt = f"""
        You are the Master AI Router for an Enterprise Decision Intelligence OS.
        Classify the following user input into one of the strict intent categories.
        
        Rules:
        - Use 'Decision' ONLY if the user is asking for a strategic choice, evaluation, or multi-factor business decision.
        - Use 'Emergency' if there is an urgent crisis (e.g., revenue drop, crash).
        - Use 'Analytics' if the user asks for historical data, charts, or benchmarks.
        - Use 'Greeting' or 'Conversation' for casual chat.
        
        User Input: "{user_input}"
        """
        
        print(f"🚦 [MasterRouter] Classifying input...")
        result = generate_json(prompt, schema)
        return result

    def route_request(self, user_input: str) -> dict:
        classification = self.classify_intent(user_input)
        intent_str = classification.get("intent", "Conversation")
        
        print(f"✅ [MasterRouter] Intent classified as: {intent_str} (Confidence: {classification.get('confidence')})")
        
        # Route to appropriate engine
        if intent_str == IntentType.DECISION.value:
            print("🚀 [MasterRouter] Routing to DECISION PIPELINE (Phase 2)...")
            return {"status": "routed", "type": "Decision", "target": "Decision Intelligence Engine"}
            
        elif intent_str == IntentType.GREETING.value:
            return intent_handlers.handle_greeting(user_input)
            
        elif intent_str == IntentType.CONVERSATION.value:
            return intent_handlers.handle_conversation(user_input)
            
        elif intent_str == IntentType.ANALYTICS.value:
            return intent_handlers.handle_analytics(user_input)
            
        elif intent_str == IntentType.EMERGENCY.value:
            return intent_handlers.handle_emergency(user_input)
            
        else:
            return intent_handlers.handle_fallback(intent_str, user_input)

master_router = MasterRouter()
