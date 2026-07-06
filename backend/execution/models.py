from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskNode(BaseModel):
    task_id: str
    plugin_name: str
    action_name: str
    dependencies: List[str] # List of task_ids that must complete first
    inputs: Dict[str, Any]
    status: str = "PENDING" # PENDING, RUNNING, SUCCESS, FAILED, ROLLBACK_SUCCESS, ROLLBACK_FAILED
    retry_count: int = 0
    max_retries: int = 3
    rollback_steps: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    audit_trail: List[str] = Field(default_factory=list)

class ExecutionPlan(BaseModel):
    plan_id: str
    goal: str
    tasks: List[TaskNode]
    priority: str
    owner: str
    estimated_duration_ms: int
    risk_level: str
    success_criteria: List[str]

class WorkflowState(BaseModel):
    workflow_id: str
    decision_id: str
    plan: ExecutionPlan
    status: str = "PENDING_APPROVAL" # PENDING_APPROVAL, RUNNING, PAUSED, SUCCESS, FAILED, FAILED_FATAL
    approval_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_task_index: int = 0
    created_at: str
    updated_at: str

class ApprovalPolicy(BaseModel):
    policy_id: str
    domain: str
    approval_mode: str # MANUAL, AUTO, MANAGER, MULTI_LEVEL, EMERGENCY
    financial_limit: Optional[float] = None
    blocked_actions: List[str] = Field(default_factory=list)
