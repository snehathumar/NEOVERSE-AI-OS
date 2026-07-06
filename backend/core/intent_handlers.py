class IntentHandlers:
    """
    Lightweight handlers for non-decision intents.
    Prevents triggering heavy simulations for casual queries.
    """
    def handle_greeting(self, user_input: str) -> dict:
        return {
            "status": "handled",
            "type": "Greeting",
            "message": "Hello! I am NEOVERSE AI OS. How can I assist you with your business decisions today?"
        }

    def handle_conversation(self, user_input: str) -> dict:
        return {
            "status": "handled",
            "type": "Conversation",
            "message": "I'm ready to discuss. However, if you need a strategic decision, please ask me to evaluate a specific business scenario."
        }

    def handle_analytics(self, user_input: str) -> dict:
        return {
            "status": "routed",
            "type": "Analytics",
            "message": "Routing to the Enterprise Analytics Dashboard for BigQuery visualization..."
            # In a full system, this triggers a redirect or loads the Analytics Engine
        }

    def handle_emergency(self, user_input: str) -> dict:
        return {
            "status": "routed",
            "type": "Emergency",
            "message": "Emergency Intent Detected! Activating Emergency Mode and generating Recovery Plan..."
            # Routes to Phase 7 Emergency Engine
        }
    
    def handle_fallback(self, intent: str, user_input: str) -> dict:
        return {
            "status": "handled",
            "type": intent,
            "message": f"Processed lightweight intent: {intent}. No heavy simulations triggered."
        }

intent_handlers = IntentHandlers()
