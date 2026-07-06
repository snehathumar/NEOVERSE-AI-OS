from typing import Dict, Any
from backend.llm_client import generate_json

UNDERSTANDING_SCHEMA = {
    "type": "object",
    "properties": {
        "industry": {"type": "string"},
        "business_model": {"type": "string"},
        "company_size": {"type": "string"},
        "growth_stage": {"type": "string"},
        "revenue_model": {"type": "string"},
        "target_customers": {"type": "string"},
        "decision_context": {"type": "string"},
        "strategic_objectives": {
            "type": "array",
            "items": {"type": "string"}
        },
        "decision_type": {
            "type": "string",
            "enum": [
                "Pricing", "Hiring", "Marketing", "Sales", "Expansion",
                "Investment", "Product", "Operations", "Finance", "HR",
                "Technology", "Legal", "Customer Success", "Startup Strategy",
                "Enterprise Strategy", "Crisis Management"
            ]
        }
    },
    "required": [
        "industry", "business_model", "company_size", "growth_stage",
        "revenue_model", "target_customers", "decision_context",
        "strategic_objectives", "decision_type"
    ]
}

class BusinessUnderstandingEngine:
    """
    Step 1-3: Business Context Understanding, Intent Validation, Decision Classification.
    """
    def execute(self, user_input: str, business_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        You are the NEOVERSE Enterprise Decision Intelligence Engine.
        Analyze the business context for the following decision request.
        
        Request: "{user_input}"
        Known State: {business_state}
        
        Determine the industry, business model, growth stage, revenue model, 
        and explicitly categorize this decision into one of the allowed types.
        """
        return generate_json(prompt, UNDERSTANDING_SCHEMA)
