from backend.llm_client import generate_json

class OpportunityEngine:
    """
    Proactively scans for adjacent opportunities based on current state.
    """
    def scan_opportunities(self, business_state: dict) -> list[dict]:
        schema = {
            "type": "object",
            "properties": {
                "opportunities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "expected_revenue_impact": {"type": "string"},
                            "risk": {"type": "string", "enum": ["Low", "Medium", "High"]},
                            "effort": {"type": "string", "enum": ["Low", "Medium", "High"]}
                        },
                        "required": ["title", "description", "expected_revenue_impact", "risk", "effort"]
                    }
                }
            },
            "required": ["opportunities"]
        }
        prompt = f"""
Given this business state, proactively find 3 hidden strategic opportunities.
Business State: {business_state}
"""
        res = generate_json(prompt, schema)
        return res.get("opportunities", [])

opportunity_engine = OpportunityEngine()
