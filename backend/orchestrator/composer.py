from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.orchestrator.context_builder import UnifiedContext
from backend.orchestrator.planner import ExecutionPlan

COMPOSER_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "business_understanding": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {"type": "string"}
        },
        "risks": {
            "type": "array",
            "items": {"type": "string"}
        },
        "debate_summary": {"type": "string"},
        "recommendation": {"type": "string"},
        "confidence": {"type": "integer"},
        "next_actions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "natural_response": {
            "type": "string",
            "description": "If this was just a chat or simple request, provide the direct conversational response here."
        }
    },
    "required": ["natural_response"]
}

class ResponseComposer:
    """
    Merges outputs from all executed modules into a single, unified, structured response.
    Never exposes raw JSON to the frontend without passing it through this composer.
    """
    
    def compose(self, context: UnifiedContext, plan: ExecutionPlan, results: Dict[str, Any]) -> Dict[str, Any]:
        # If it's interview mode, we just want to ask for the missing fields.
        if plan.is_interview_mode:
            return {
                "natural_response": f"To provide a highly accurate analysis, I need a few more details: {', '.join(plan.missing_fields)}. Could you clarify those?",
                "is_interview": True,
                "missing_fields": plan.missing_fields
            }
            
        # For a standard execution, compile the results
        prompt = f"""
        You are NEOVERSE AI's Executive Composer.
        Your task is to read the raw JSON outputs from the backend execution modules and compile them into a beautiful, cohesive, and deeply insightful final response.
        
        User Input: "{context.user_input}"
        
        Module Outputs:
        {results}
        
        If this is a simple conversation or question, just populate 'natural_response'.
        If this is a complex business decision, leave 'natural_response' empty and fill out the executive summary, recommendation, risks, evidence, etc.
        """
        
        composed = generate_json(prompt, COMPOSER_SCHEMA)
        
        # We attach the raw results as metadata, which frontend can use for charts or Judge Mode
        composed["_raw_module_outputs"] = results
        return composed
