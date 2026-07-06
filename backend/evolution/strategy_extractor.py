from typing import Dict, Any, List
import uuid
from backend.evolution.models import StrategyPattern
from backend.llm_client import generate_json

class StrategyExtractor:
    """
    Extracts reusable Strategy Patterns from a completed decision lifecycle.
    """
    def extract_strategies(self, 
                           decision_context: dict, 
                           outcome: str, 
                           business_domain: str) -> List[StrategyPattern]:
        
        prompt = f"""
        You are the NEOVERSE Strategy Extraction Engine.
        Analyze the following decision context and outcome.
        
        Domain: {business_domain}
        Outcome: {outcome}
        Context: {decision_context}
        
        Extract 1-3 highly reusable Strategy Patterns (Playbooks) from this experience.
        Identify the core assumptions that must hold, the risks, and the expected outcome.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "strategies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "industry": {"type": "string"},
                            "conditions": {"type": "array", "items": {"type": "string"}},
                            "assumptions": {"type": "array", "items": {"type": "string"}},
                            "risks": {"type": "array", "items": {"type": "string"}},
                            "expected_outcome": {"type": "string"}
                        },
                        "required": ["industry", "conditions", "assumptions", "risks", "expected_outcome"]
                    }
                }
            },
            "required": ["strategies"]
        }
        
        res = generate_json(prompt, schema)
        extracted = res.get("strategies", [])
        
        patterns = []
        for s in extracted:
            s["strategy_id"] = str(uuid.uuid4())
            s["business_domain"] = business_domain
            s["actual_outcome"] = outcome
            s["confidence"] = 75
            s["success_rate"] = 100 if outcome == "Success" else 0
            s["reusability_score"] = 80
            patterns.append(StrategyPattern(**s))
            
        return patterns
