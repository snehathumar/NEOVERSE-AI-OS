import pandas as pd
from backend.llm_client import generate_json
import json

TIMELINE_SCHEMA = {
    "type": "object",
    "properties": {
        "universes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "period": {"type": "string", "enum": ["Today", "30 Days", "90 Days", "6 Months", "1 Year"]},
                                "revenue": {"type": "string", "description": "Include currency units, e.g., $10k"},
                                "customers": {"type": "string", "description": "Include %, e.g., +5%"},
                                "risk": {"type": "string", "description": "Include %, e.g., 20%"},
                                "cash_flow": {"type": "string"},
                                "market_position": {"type": "string"}
                            },
                            "required": ["period", "revenue", "customers", "risk", "cash_flow", "market_position"]
                        }
                    }
                },
                "required": ["name", "timeline"]
            }
        }
    },
    "required": ["universes"]
}

def generate_timelines(decision: str, domain: str, universes_summary: list):
    prompt = f"""
Based on the following 1-year simulated Universes for a {domain} facing the decision: "{decision}", 
generate a temporal timeline mapping the progression at Today, 30 Days, 90 Days, 6 Months, and 1 Year for each Universe.

Universes Summary:
{json.dumps(universes_summary, indent=2)}

You must return numerical metrics WITH UNITS (e.g., $5,000, 15%, +200 customers).
"""
    return generate_json(prompt, TIMELINE_SCHEMA)
