from backend.intelligence.plugin_base import IntelligencePlugin
from typing import Dict, Any

class DigitalTwinPlugin(IntelligencePlugin):
    """
    Plugin-based Business Digital Twin.
    Contains expanded business profile tracking: Revenue, Customers, Products, 
    Pricing, Expenses, Employees, Growth, Market, Competition, Risk.
    """
    
    def __init__(self):
        self._state = {}

    def initialize(self, config: Dict[str, Any]):
        print("🏢 [DigitalTwin] Initializing virtual business clone...")
        # Default starting state for simulations
        self._state = {
            "business_profile": "Enterprise SaaS",
            "revenue": 10000000,
            "customers": 50000,
            "products": 3,
            "pricing": 200,
            "expenses": 4000000,
            "employees": 120,
            "growth_rate": 1.15,
            "market_share": 12.5,
            "competition": "High",
            "risk_index": 45
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        The DigitalTwin doesn't 'execute' decisions itself; it accepts a state mutation 
        and returns the current snapshot.
        """
        mutation = payload.get("mutation", {})
        for k, v in mutation.items():
            if k in self._state:
                self._state[k] = v
                
        return self._state

    def validate(self, result: Dict[str, Any]) -> bool:
        return "revenue" in result and "risk_index" in result

    def serialize(self) -> Dict[str, Any]:
        return {
            "module": "DigitalTwin",
            "data": self._state
        }
