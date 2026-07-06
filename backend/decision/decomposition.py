from typing import Dict, Any, List
from backend.llm_client import generate_json

DECOMPOSITION_SCHEMA = {
    "type": "object",
    "properties": {
        "root_causes": {
            "type": "array",
            "items": {"type": "string"}
        },
        "constraints": {
            "type": "array",
            "items": {"type": "string"}
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "external_factors": {
            "type": "array",
            "items": {"type": "string"}
        },
        "internal_factors": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["root_causes", "constraints", "dependencies", "external_factors", "internal_factors"]
}

class ProblemDecompositionEngine:
    """
    Step 4: Problem Decomposition
    """
    def execute(self, user_input: str, understanding: Dict[str, Any]) -> Dict[str, List[str]]:
        prompt = f"""
        You are the NEOVERSE Enterprise Decision Intelligence Engine.
        Break down the following complex business problem into independent reasoning blocks.
        
        Request: "{user_input}"
        Business Understanding Context: {understanding}
        
        Identify:
        - Root Causes driving this decision
        - Constraints (budget, time, regulations)
        - Dependencies (what must happen first)
        - External Macro/Micro Factors
        - Internal Organizational Factors
        """
        return generate_json(prompt, DECOMPOSITION_SCHEMA)
