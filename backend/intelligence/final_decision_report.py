from typing import Dict, Any
import json
from backend.intelligence.dependency_graph.engine import DependencyGraphPlugin
from backend.intelligence.evidence_engine.engine import EvidenceTrustPlugin
from backend.intelligence.digital_twin.engine import DigitalTwinPlugin
from backend.intelligence.simulation_lab.engine import SimulationLabPlugin
from backend.intelligence.reasoning_trace.engine import ReasoningTracePlugin

class DecisionReportAggregator:
    """
    Orchestrates the independent plugins and aggregates their serialized 
    outputs into the Final Decision Report as requested in Phase 11.
    """
    
    def __init__(self):
        self.plugins = [
            DependencyGraphPlugin(),
            EvidenceTrustPlugin(),
            DigitalTwinPlugin(),
            SimulationLabPlugin(),
            ReasoningTracePlugin()
        ]
        
    def generate_report(self, decision_payload: Dict[str, Any]) -> str:
        report = {}
        
        # 1. Initialize
        for plugin in self.plugins:
            plugin.initialize({})
            
        # 2. Execute
        for plugin in self.plugins:
            plugin.execute(decision_payload)
            
        # 3. Serialize and Aggregate
        for plugin in self.plugins:
            serialized = plugin.serialize()
            report[serialized["module"]] = serialized["data"]
            
        # 4. Final Finalization (Appending overall metadata)
        final_report = {
            "Final Recommendation": "Proceed with price increase.",
            "Aggregated Intelligence": report
        }
        
        return json.dumps(final_report, indent=4)

decision_report_aggregator = DecisionReportAggregator()
