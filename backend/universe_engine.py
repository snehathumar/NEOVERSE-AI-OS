from backend.llm_client import generate_json

UNIVERSE_SCHEMA = {
    "type": "object",
    "properties": {
        "universes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "enum": ["Universe Alpha (Best Case)", "Universe Beta (Balanced Case)", "Universe Gamma (Worst Case)"]
                    },
                    "revenue": {
                        "type": "string",
                        "description": "Calculated revenue impact (e.g. '+15%', '-5%')."
                    },
                    "risk": {
                        "type": "string",
                        "description": "Assessed risk level (e.g. 'Low', 'High')."
                    },
                    "customer_impact": {
                        "type": "string",
                        "description": "How customers are affected."
                    },
                    "timeline": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Milestones expected in this universe (e.g. Month 1, Month 3)."
                    },
                    "assumptions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific conditions required for this universe to occur."
                    },
                    "confidence": {
                        "type": "integer",
                        "description": "Probability/Confidence (0-100) of this universe occurring."
                    },
                    "calculation_reasoning": {
                        "type": "string",
                        "description": "Explicit step-by-step mathematical reasoning for how the revenue and risk were calculated. Do not use random numbers."
                    }
                },
                "required": [
                    "name", "revenue", "risk", "customer_impact", 
                    "timeline", "assumptions", "confidence", "calculation_reasoning"
                ]
            },
            "minItems": 3,
            "maxItems": 3
        }
    },
    "required": ["universes"]
}

class ParallelUniverseEngine:
    """
    Parallel Universe Engine.
    Generates deterministic Best, Balanced, and Worst case scenarios.
    Never uses random numbers; relies on explicit, explainable calculations.
    """
    def __init__(self):
        pass

    def simulate_decision(self, decision_context: str, business_state: dict) -> dict:
        """
        Simulates the decision across three distinct universes.
        """
        prompt = f"""
You are the Parallel Universe Engine.
A business is evaluating the following decision: "{decision_context}"
Business Profile: {business_state}

You must simulate exactly 3 universes:
1. Universe Alpha (Best Case)
2. Universe Beta (Balanced Case)
3. Universe Gamma (Worst Case)

CRITICAL RULES:
1. NEVER generate random numbers. 
2. You must mathematically calculate the revenue impacts based on standard industry baselines and explicitly explain your calculations in 'calculation_reasoning'.
3. Detail the Revenue, Risk, Customer Impact, Timeline, Assumptions, and Confidence for each universe.

Return strictly JSON matching the schema.
"""
        try:
            result = generate_json(prompt, UNIVERSE_SCHEMA)
            # Ensure it returns exactly what is requested, or fallback
            if "universes" not in result or len(result["universes"]) != 3:
                raise ValueError("LLM did not return exactly 3 universes.")
            return result
        except Exception as e:
            print(f"[Universe Engine] Failed to simulate universes: {e}")
            return {"error": "Simulation failed. Could not generate deterministic universes."}

# Global singleton
universe_engine = ParallelUniverseEngine()
