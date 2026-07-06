import asyncio
from typing import Dict, Any

from backend.simulation.digital_twin import DigitalTwinEngine
from backend.simulation.scenario_library import ScenarioLibrary
from backend.simulation.simulator import AIHeuristicSimulator
from backend.simulation.analyzer import SimulationAnalyzer
from backend.simulation.models import SimulationTrace
from backend.memory.manager import MemoryManager
from backend.platform.cloud.logging_provider import cloud_logger

class SimulationEngine:
    """
    Core engine for Enterprise Digital Twin & Multi-Universe Simulation.
    """
    def __init__(self):
        self.digital_twin_engine = DigitalTwinEngine()
        self.simulator = AIHeuristicSimulator() # Can be swapped with other providers
        self.analyzer = SimulationAnalyzer()
        self.memory = MemoryManager()

    def _determine_time_horizon(self, decision_type: str) -> int:
        """Determines simulation horizon based on decision type. Returns months."""
        mapping = {
            "Operational": 1,
            "Marketing": 3,
            "Hiring": 6,
            "Pricing": 12,
            "Expansion": 36,
            "Strategic transformation": 60
        }
        return mapping.get(decision_type, 12) # Default 1 year

    async def execute_simulation(self, decision_context: dict, business_state: dict) -> Dict[str, Any]:
        cloud_logger.info("Starting Multi-Universe Simulation Pipeline")
        
        # 1. Load / Create Digital Twin
        current_twin_memory = self.memory.get_digital_twin()
        current_twin_state = current_twin_memory.model_dump() if current_twin_memory else None
        
        digital_twin = self.digital_twin_engine.build_snapshot(business_state, current_twin_state)
        cloud_logger.info("Digital Twin synchronized.")
        
        # 2. Determine Time Horizon
        decision_type = decision_context.get("business_understanding", {}).get("decision_type", "Strategy")
        time_horizon = self._determine_time_horizon(decision_type)
        
        # 3. Create Universes (Scenarios)
        scenarios = ScenarioLibrary.get_standard_scenarios()
        
        # 4. Execute Parallel Simulations
        cloud_logger.info(f"Simulating {len(scenarios)} parallel universes over {time_horizon} months...")
        
        tasks = []
        for scenario in scenarios:
            tasks.append(
                self.simulator.simulate_universe(
                    scenario_name=scenario,
                    time_horizon_months=time_horizon,
                    digital_twin_state=digital_twin.model_dump(),
                    decision_context=decision_context
                )
            )
            
        universes = await asyncio.gather(*tasks)
        
        # 5. Analyze and Compare
        cloud_logger.info("Conducting Sensitivity Analysis & Ranking")
        sensitivity = self.analyzer.execute(universes)
        recommended_scenario = self.analyzer.rank_universes(universes)
        
        # 6. Build final trace
        trace = SimulationTrace(
            digital_twin=digital_twin,
            universes=universes,
            sensitivity_analysis=sensitivity,
            recommended_scenario=recommended_scenario,
            learning_insights={} # To be populated post-execution
        )
        
        return trace.model_dump()
