from backend.llm_client import generate_json
import json

RADAR_SCHEMA = {
    "type": "object",
    "properties": {
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "expected_impact": {"type": "string"},
                    "confidence": {"type": "string"},
                    "priority": {"type": "string", "enum": ["High", "Medium", "Low"]}
                }
            }
        },
        "risks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "warning": {"type": "string"},
                    "expected_cost_increase": {"type": "string"},
                    "suggested_actions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "priority": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"]}
                }
            }
        }
    },
    "required": ["opportunities", "risks"]
}

ROOT_CAUSE_SCHEMA = {
    "type": "object",
    "properties": {
        "investigations": {
            "type": "array",
            "items": {"type": "string"}
        },
        "root_cause_found": {"type": "string"},
        "contributions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "factor": {"type": "string"},
                    "percentage": {"type": "string"}
                }
            }
        },
        "recommendation": {"type": "string"}
    },
    "required": ["investigations", "root_cause_found", "contributions", "recommendation"]
}

def scan_for_opportunities_and_risks(business_profile: dict, kpis: dict, market_signals: dict):
    prompt = f"""
Business Profile: {business_profile}
Current KPIs: {kpis}
Today's Market Signals: {json.dumps(market_signals)}

You are an Autonomous Business OS. Scan the market signals and KPIs.
Detect hidden Revenue/Cost/Marketing opportunities. Ensure they have realistic expected impacts with units.
Detect looming Risks (e.g., inflation, weather, supply chain). If the impact is > 5%, raise an alert. Ignore minor < 1% fluctuations.

Return strictly conforming to the schema.
"""
    return generate_json(prompt, RADAR_SCHEMA)

def investigate_root_cause(issue: str, business_profile: dict, market_signals: dict):
    prompt = f"""
The business is experiencing an issue: "{issue}"
Business Profile: {business_profile}
Recent Market Signals: {json.dumps(market_signals)}

Act as a Root Cause Investigator.
1. List the factors you are investigating (Weather, Pricing, Competitor, etc.).
2. State the Root Cause Found (a combination of events).
3. Provide the estimated contribution breakdown (e.g. Competition: 63%, Weather: 24%).
4. Provide a clear recommendation to fix it.
"""
    return generate_json(prompt, ROOT_CAUSE_SCHEMA)
