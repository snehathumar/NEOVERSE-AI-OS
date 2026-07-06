from backend.orchestrator.modules.base import ExecutionModule
from backend.simulation.engine import SimulationEngine
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class SimulationModule(ExecutionModule):
    """
    Wraps the Phase 8 Enterprise Digital Twin & Multi-Universe Simulation Engine.
    """
    def __init__(self):
        self.simulation_engine = SimulationEngine()
        self.bq = BigQueryProvider()
        
    @property
    def name(self) -> str:
        return "SimulationModule"

    @property
    def is_critical(self) -> bool:
        return True

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Require upstream decision output to run simulation
        # It should run after DebateModule if present, or DecisionModule directly
        if "DecisionModule" not in context.get("upstream_results", {}):
            return False
        return True

    async def execute(self, context: dict) -> dict:
        decision_context = context["upstream_results"]["DecisionModule"]
        business_state = context.get("business_state", {})
        
        # We only simulate if it's not a missing info trap
        if decision_context.get("is_interview"):
            return {"status": "skipped", "reason": "Decision engine requires interview."}
            
        sim_result = await self.simulation_engine.execute_simulation(decision_context, business_state)
        
        # Async stream analytics to BigQuery
        try:
            self.bq.stream_analytics("simulation_sessions", {
                "session_id": context.get("session_id"),
                "recommended_scenario": sim_result.get("recommended_scenario"),
                "stability_index": sim_result.get("sensitivity_analysis", {}).get("stability_index"),
                "decision_robustness_score": sim_result.get("sensitivity_analysis", {}).get("decision_robustness_score")
            })
        except Exception as e:
            cloud_logger.warning(f"Failed to stream simulation analytics: {e}")
            
        return sim_result

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
