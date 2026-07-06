import asyncio
from backend.orchestrator.modules.base import ExecutionModule
from backend.evolution.engine import SelfEvolutionEngine
from backend.platform.cloud.logging_provider import cloud_logger

class SelfEvolutionModule(ExecutionModule):
    """
    Wraps the Phase 11 Enterprise Self-Evolution & Continuous Learning Engine.
    Executes as a fire-and-forget background task after Reporting is complete.
    """
    def __init__(self):
        self.evolution_engine = SelfEvolutionEngine()
        
    @property
    def name(self) -> str:
        return "SelfEvolutionModule"

    @property
    def is_critical(self) -> bool:
        # Non-critical because it runs post-decision and shouldn't block the user
        return False

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Requires decision to have completed
        return "DecisionModule" in context.get("upstream_results", {})

    async def execute(self, context: dict) -> dict:
        # We fire and forget the evolution loop. 
        # It runs in the background so the router can return immediately.
        cloud_logger.info("Dispatching SelfEvolutionEngine in the background...")
        
        asyncio.create_task(
            self.evolution_engine.execute_evolution(context)
        )
        
        # Return immediately to unblock the HTTP response
        return {"status": "backgrounded"}

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
