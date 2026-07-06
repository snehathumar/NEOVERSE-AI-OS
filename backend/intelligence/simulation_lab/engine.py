from backend.intelligence.plugin_base import IntelligencePlugin
from backend.intelligence.digital_twin.engine import DigitalTwinPlugin
from typing import Dict, Any
import copy

class SimulationLabPlugin(IntelligencePlugin):
    """
    Plugin-based Simulation Lab.
    Handles Multiple Universes, 'What-if' experiments, side-by-side comparisons, and confidence evolution.
    """
    
    def __init__(self):
        self._simulation_results = {}
        self.digital_twin = DigitalTwinPlugin()
        self.digital_twin.initialize({})

    def initialize(self, config: Dict[str, Any]):
        print("🧪 [SimulationLab] Initializing simulation environment...")
        self._simulation_results = {}

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        modifications = payload.get("modifications", {})
        print(f"🧪 [SimulationLab] Running multiple universe simulations on variables: {list(modifications.keys())}")
        
        baseline_state = copy.deepcopy(self.digital_twin.execute({}))
        
        # Simulate Best Case (Optimistic bounds)
        best_case = copy.deepcopy(baseline_state)
        best_case["revenue"] = int(baseline_state["revenue"] * 1.3)
        best_case["risk_index"] = max(0, baseline_state["risk_index"] - 10)
        
        # Simulate Expected Case
        expected_case = copy.deepcopy(baseline_state)
        for k, v in modifications.items():
            expected_case[k] = v
        # basic propagation mock
        if "pricing" in modifications:
            expected_case["revenue"] = int(expected_case["revenue"] * 1.1)
            
        # Simulate Worst Case
        worst_case = copy.deepcopy(baseline_state)
        worst_case["revenue"] = int(baseline_state["revenue"] * 0.8)
        worst_case["risk_index"] = min(100, baseline_state["risk_index"] + 20)
        
        self._simulation_results = {
            "baseline": baseline_state,
            "universes": {
                "best_case": best_case,
                "expected_case": expected_case,
                "worst_case": worst_case
            },
            "confidence_evolution": {
                "initial": 80,
                "post_simulation": 88
            }
        }
        return self._simulation_results

    def validate(self, result: Dict[str, Any]) -> bool:
        return "universes" in result

    def serialize(self) -> Dict[str, Any]:
        return {
            "module": "SimulationLab",
            "data": self._simulation_results
        }
