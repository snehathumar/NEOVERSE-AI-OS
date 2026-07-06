from backend.orchestrator.modules.base import ExecutionModule
from backend.decision.engine import EnterpriseDecisionEngine

class DecisionModule(ExecutionModule):
    """
    Wraps the Phase 6 Enterprise Decision Intelligence Engine.
    Executes the 23-step reasoning pipeline.
    """
    def __init__(self):
        self.decision_engine = EnterpriseDecisionEngine()
        
    @property
    def name(self) -> str:
        return "DecisionModule"

    @property
    def is_critical(self) -> bool:
        return True

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        return True

    async def execute(self, context: dict) -> dict:
        user_input = context.get("user_input", "")
        business_state = context.get("business_state", {})
        upstream_results = context.get("upstream_results", {})
        
        # We pass upstream results (like Memory/Research) to be scored by Evidence Engine
        return await self.decision_engine.execute_decision(user_input, business_state, upstream_results)

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
