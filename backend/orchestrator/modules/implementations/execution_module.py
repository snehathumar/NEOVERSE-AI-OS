import asyncio
from backend.orchestrator.modules.base import ExecutionModule
from backend.execution.engine import WorkflowEngine
from backend.platform.cloud.logging_provider import cloud_logger

class ExecutionEngineModule(ExecutionModule):
    """
    Wraps the Phase 12 Enterprise Execution Engine.
    Executes asynchronously as the final stage of the pipeline to transform the approved recommendation into real-world action.
    """
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        
    @property
    def name(self) -> str:
        return "ExecutionModule"

    @property
    def is_critical(self) -> bool:
        # Non-critical to the HTTP response, runs in background to await approval or execute.
        return False

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # Requires a decision to have been made
        return "DecisionModule" in context.get("upstream_results", {})

    async def execute(self, context: dict) -> dict:
        cloud_logger.info("Initializing Execution Workflow from Decision Context...")
        
        # We extract the upstream decision
        decision_context = context.get("upstream_results", {}).get("DecisionModule", {})
        
        # Generate the Plan and put it in PENDING_APPROVAL (or execute if AUTO)
        workflow_state = await self.workflow_engine.initialize_workflow(decision_context)
        
        # If policy allows immediate execution, dispatch it in the background
        if workflow_state.get("status") in ["APPROVED", "AUTO"]:
            asyncio.create_task(
                self.workflow_engine.execute_workflow(workflow_state["workflow_id"], is_dry_run=False)
            )
            
        return {
            "status": "initialized",
            "workflow_id": workflow_state.get("workflow_id"),
            "execution_status": workflow_state.get("status")
        }

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
