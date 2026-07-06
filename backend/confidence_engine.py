from backend.llm_client import generate_json

CONFIDENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "confidence_score": {
            "type": "string",
            "description": "Confidence percentage WITH unit, e.g., '74%'"
        },
        "reason_high": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Reasons increasing confidence (e.g. 'Historical data', 'Provided parameters')"
        },
        "reason_low": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Missing factors decreasing confidence (e.g. 'Customer demographics missing')"
        }
    },
    "required": ["confidence_score", "reason_high", "reason_low"]
}

def calculate_dynamic_confidence(known_data: dict, assumptions: list):
    prompt = f"""
Calculate the simulation confidence score based on the ratio of known data to assumptions.

Known Data Provided by User: {known_data}
Assumptions Made by Engine: {assumptions}

If there are many assumptions and little known data, confidence should be low (e.g. 40-60%).
If the user provided extensive data, confidence should be high (e.g. 80-95%).
Never output 100%.

List factors increasing confidence and factors decreasing confidence.
"""
    return generate_json(prompt, CONFIDENCE_SCHEMA)
