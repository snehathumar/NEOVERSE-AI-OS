from typing import Dict, Any
from backend.llm_client import generate_json
from backend.simulation.models import DigitalTwinSnapshot
from datetime import datetime, timezone

class DigitalTwinEngine:
    """
    Constructs and updates the Business Digital Twin using existing MemoryContext
    and the new Business Context passed by the Router.
    """
    def build_snapshot(self, business_state: dict, current_twin_state: dict = None) -> DigitalTwinSnapshot:
        prompt = f"""
        You are the NEOVERSE Digital Twin Engine.
        Synthesize the current state of the business into a structured Digital Twin Snapshot.
        
        Current Knowledge Base & Context:
        {business_state}
        
        Previous Digital Twin State (if any):
        {current_twin_state}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "business_profile": {"type": "object", "additionalProperties": {"type": "string"}},
                "organization_structure": {"type": "object", "additionalProperties": {"type": "string"}},
                "financial_snapshot": {"type": "object", "additionalProperties": {"type": "string"}},
                "operational_kpis": {"type": "object", "additionalProperties": {"type": "string"}},
                "market_position": {"type": "string"},
                "strategic_goals": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["business_profile", "organization_structure", "financial_snapshot", "operational_kpis", "market_position", "strategic_goals"]
        }
        
        res = generate_json(prompt, schema)
        
        return DigitalTwinSnapshot(
            business_profile=res["business_profile"],
            organization_structure=res["organization_structure"],
            financial_snapshot=res["financial_snapshot"],
            operational_kpis=res["operational_kpis"],
            market_position=res["market_position"],
            strategic_goals=res["strategic_goals"],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
