from backend.llm_client import generate_json

ASSUMPTION_ENGINE_SCHEMA = {
    "type": "object",
    "properties": {
        "assumptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "parameter": {"type": "string"},
                    "assumed_value": {"type": "string"}
                },
                "required": ["parameter", "assumed_value"]
            }
        }
    },
    "required": ["assumptions"]
}

def generate_assumptions(decision: str, domain: str, known_data: dict, required_parameters: list):
    prompt = f"""
Decision: "{decision}"
Domain: {domain}
Known Data: {known_data}
Required Parameters: {required_parameters}

We are going to simulate this scenario but we are missing some parameters.
Generate reasonable, realistic assumptions for the missing parameters, as well as general environmental variables (e.g. Inflation, Season, Competition, Weather if relevant).
Return a list of assumptions.
"""
    return generate_json(prompt, ASSUMPTION_ENGINE_SCHEMA)
