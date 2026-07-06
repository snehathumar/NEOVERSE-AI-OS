from backend.llm_client import generate_json

DOMAIN_DETECTOR_SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {"type": "string"},
        "required_parameters": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of core business parameters needed to simulate this domain (e.g. Current Price, Daily Customers, Competitors, Monthly Revenue)."
        },
        "reasoning_framework": {
            "type": "string",
            "description": "How the AI should reason about this specific domain (e.g. focus on table turnover, office crowd, inventory expiry)."
        }
    },
    "required": ["domain", "required_parameters", "reasoning_framework"]
}

def detect_domain_and_params(decision: str):
    prompt = f"""
Analyze the following business decision:
"{decision}"

1. Identify the specific domain/industry (e.g. Coffee Shop, Restaurant, Kirana, Salon).
2. List 4 to 6 critical business parameters required to simulate this decision mathematically (e.g. Current Price, Daily Footfall, Competitor Density, Profit Margin).
3. Provide a brief reasoning framework on what matters most in this domain.

Return strictly matching the JSON schema.
"""
    return generate_json(prompt, DOMAIN_DETECTOR_SCHEMA)
