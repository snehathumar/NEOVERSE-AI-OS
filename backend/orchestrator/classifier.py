from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.orchestrator.context_builder import UnifiedContext

INTENT_CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "Greeting", "General Chat", "Research", "Learning", 
                "Business Analysis", "Decision Making", "Brainstorming", 
                "Risk Analysis", "Strategy", "Simulation", "Debate", 
                "Report Generation", "Data Analysis", "Emergency", 
                "Follow-up Conversation", "Memory Query", "File Analysis"
            ]
        },
        "confidence": {"type": "integer"},
        "alternative_intents": {
            "type": "array",
            "items": {"type": "string"}
        },
        "business_domain": {"type": "string"},
        "complexity": {
            "type": "string",
            "enum": ["Low", "Medium", "High", "Critical"]
        },
        "urgency": {
            "type": "string",
            "enum": ["Low", "Medium", "High", "Immediate"]
        },
        "missing_information": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of missing critical parameters required to fulfill the intent (e.g. for a Business Decision: missing budget, target market)."
        },
        "required_modules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of module names (e.g., 'DecisionEngine', 'DebateEngine', 'RiskEngine') deemed necessary."
        }
    },
    "required": ["intent", "confidence", "complexity", "urgency", "missing_information", "required_modules"]
}

class IntentClassifier:
    """
    Classifies the user's intent based on input and UnifiedContext.
    """
    
    def classify(self, context: UnifiedContext) -> Dict[str, Any]:
        
        # Prepare context representation
        learnings_summary = ", ".join([f"Learned: {', '.join(l.lessons_learned)}" for l in context.relevant_learnings])
        
        prompt = f"""
        You are the NEOVERSE Enterprise AI Router Classifier.
        Analyze the user's input and classify their exact intent.
        
        Consider the following context:
        - Recent Conversation History: {context.conversation_history[-3:] if context.conversation_history else 'None'}
        - Relevant Past Learnings: {learnings_summary}
        - User Input: "{context.user_input}"
        
        Determine the intent, complexity, urgency, and any missing information.
        If the user is asking to make a major decision but hasn't provided key context (like budget, goals), explicitly list those in missing_information.
        Recommend which backend modules should be executed (e.g., 'DecisionEngine', 'RiskEngine', 'ReportGenerator', 'ChatModule').
        """
        
        return generate_json(prompt, INTENT_CLASSIFICATION_SCHEMA)
