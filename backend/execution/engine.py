import asyncio
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime, timezone

from backend.execution.models import WorkflowState, ExecutionPlan, TaskNode
from backend.execution.planner import ExecutionPlanner
from backend.execution.policies import ApprovalPolicyEngine
from backend.execution.plugins.rest_api import RestAPIPlugin
from backend.execution.plugins.mcp_plugin import MCPPlugin
from backend.memory.manager import StorageManager
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class WorkflowEngine:
    """
    Core engine for Phase 12: Enterprise Execution Engine & Autonomous Business Action Platform.
    Manages state persistence, DAG resolution, retries, and reverse-order rollbacks.
    """
    def __init__(self):
        self.planner = ExecutionPlanner()
        self.policy_engine = ApprovalPolicyEngine()
        self.storage_manager = StorageManager()
        self.bq = BigQueryProvider()
        
        # Load Plugins
        self.plugins = {
            "RestAPIPlugin": RestAPIPlugin(),
            "MCPPlugin": MCPPlugin()
        }

    async def initialize_workflow(self, decision_context: dict) -> Dict[str, Any]:
        """Converts a decision into a WorkflowState, checks policies, and saves it to Storage."""
        recommendation = decision_context.get("recommended_action_plan", "No action")
        domain = decision_context.get("business_understanding", {}).get("decision_type", "Default")
        decision_id = decision_context.get("decision_id", str(uuid.uuid4()))
        
        # 1. Generate Execution Plan (DAG)
        plan = self.planner.generate_plan(recommendation, decision_context)
        
        # 2. Validate against Approval Policy
        policy_result = self.policy_engine.validate_plan(plan, domain)
        
        # 3. Create initial state
        workflow_id = f"wf-{uuid.uuid4()}"
        state = WorkflowState(
            workflow_id=workflow_id,
            decision_id=decision_id,
            plan=plan,
            status="PENDING_APPROVAL" if policy_result["status"] == "REQUIRES_APPROVAL" else policy_result["status"],
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        
        if state.status == "BLOCKED":
            cloud_logger.warning(f"Workflow {workflow_id} blocked by policy.")
            state.status = "FAILED_FATAL"
            
        # 4. Persist to StorageManager
        self.storage_manager.save_json(f"workflows/{workflow_id}.json", state.model_dump())
        
        return state.model_dump()

    async def execute_workflow(self, workflow_id: str, is_dry_run: bool = False) -> Dict[str, Any]:
        """
        Executes an approved workflow. Resolves dependencies and runs plugins.
        """
        cloud_logger.info(f"Starting execution for Workflow {workflow_id} (Dry Run: {is_dry_run})")
        
        raw_state = self.storage_manager.get_json(f"workflows/{workflow_id}.json")
        if not raw_state:
            return {"error": "Workflow not found."}
            
        state = WorkflowState(**raw_state)
        
        if state.status not in ["APPROVED", "AUTO", "RUNNING"]:
            return {"error": f"Workflow is in state {state.status}, cannot execute."}
            
        state.status = "RUNNING"
        self._save_state(state)
        
        # Simple sequential resolution for V1 (ignores parallel DAG for brevity in skeleton)
        failed_task = None
        
        for task in state.plan.tasks:
            if task.status == "SUCCESS":
                continue
                
            task.status = "RUNNING"
            self._save_state(state)
            
            plugin = self.plugins.get(task.plugin_name)
            if not plugin:
                task.status = "FAILED"
                task.audit_trail.append("Plugin not found.")
                failed_task = task
                break
                
            # Execute with retries
            success = False
            for attempt in range(task.max_retries + 1):
                try:
                    if is_dry_run:
                        cloud_logger.info(f"DRY RUN: Executing {task.task_id} via {task.plugin_name}")
                        task.execution_result = {"dry_run": True}
                        success = True
                    else:
                        task.execution_result = await plugin.execute(task.action_name, task.inputs)
                        success = True
                    break
                except Exception as e:
                    cloud_logger.error(f"Task {task.task_id} failed attempt {attempt}: {e}")
                    task.retry_count = attempt
                    task.audit_trail.append(f"Failed attempt {attempt}: {e}")
                    await asyncio.sleep(2 ** attempt) # Exponential backoff
                    
            if success:
                task.status = "SUCCESS"
            else:
                task.status = "FAILED"
                failed_task = task
                break
                
            self._save_state(state)

        # Handle Failure & Rollback
        if failed_task:
            cloud_logger.error(f"Workflow {workflow_id} failed at task {failed_task.task_id}. Initiating Rollback.")
            await self._rollback_workflow(state, failed_task, is_dry_run)
            state.status = "FAILED_FATAL"
        else:
            state.status = "SUCCESS"
            
        self._save_state(state)
        
        # Analytics
        self.bq.stream_analytics("execution_history", {
            "workflow_id": state.workflow_id,
            "status": state.status,
            "is_dry_run": is_dry_run
        })
        
        return state.model_dump()

    async def _rollback_workflow(self, state: WorkflowState, failed_task: TaskNode, is_dry_run: bool):
        """Rolls back all successful tasks in reverse order."""
        for task in reversed(state.plan.tasks):
            if task.status == "SUCCESS":
                plugin = self.plugins.get(task.plugin_name)
                if plugin and task.rollback_steps:
                    try:
                        if is_dry_run:
                            cloud_logger.info(f"DRY RUN: Rolling back {task.task_id}")
                            task.status = "ROLLBACK_SUCCESS"
                        else:
                            success = await plugin.rollback(task.action_name, task.execution_result, task.rollback_steps)
                            task.status = "ROLLBACK_SUCCESS" if success else "ROLLBACK_FAILED"
                    except Exception as e:
                        cloud_logger.error(f"Rollback failed for {task.task_id}: {e}")
                        task.status = "ROLLBACK_FAILED"
                else:
                    task.status = "ROLLBACK_UNAVAILABLE"
                self._save_state(state)

    def _save_state(self, state: WorkflowState):
        state.updated_at = datetime.now(timezone.utc).isoformat()
        self.storage_manager.save_json(f"workflows/{state.workflow_id}.json", state.model_dump())
