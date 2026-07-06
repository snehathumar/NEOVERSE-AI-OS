from backend.execution.models import ApprovalPolicy, ExecutionPlan
from typing import Dict, Any

class ApprovalPolicyEngine:
    """
    Validates execution plans against enterprise governance policies.
    """
    def __init__(self):
        # In production, these would be loaded from StorageManager/Firestore
        self.policies = {
            "Finance": ApprovalPolicy(
                policy_id="pol-fin-1",
                domain="Finance",
                approval_mode="MULTI_LEVEL",
                financial_limit=10000.0,
                blocked_actions=["wire_transfer", "issue_refund"]
            ),
            "Marketing": ApprovalPolicy(
                policy_id="pol-mkt-1",
                domain="Marketing",
                approval_mode="MANAGER",
                financial_limit=5000.0,
                blocked_actions=["delete_campaign"]
            ),
            "Default": ApprovalPolicy(
                policy_id="pol-def-1",
                domain="Default",
                approval_mode="MANUAL", # Everything defaults to Manual
                financial_limit=0.0,
                blocked_actions=["*"]
            )
        }

    def validate_plan(self, plan: ExecutionPlan, domain: str) -> Dict[str, Any]:
        """
        Validates if a plan requires approval, is blocked, or can auto-execute.
        """
        policy = self.policies.get(domain, self.policies["Default"])
        
        # Check blocked actions
        for task in plan.tasks:
            if task.action_name in policy.blocked_actions or "*" in policy.blocked_actions:
                return {
                    "status": "BLOCKED",
                    "reason": f"Action {task.action_name} is blocked by policy {policy.policy_id}"
                }
                
        # In a real system, we would calculate total financial impact here.
        # For now, we enforce the approval mode
        
        if policy.approval_mode == "AUTO":
            return {"status": "APPROVED", "reason": "Policy allows auto-execution."}
            
        return {
            "status": "REQUIRES_APPROVAL",
            "mode": policy.approval_mode,
            "reason": f"Policy {policy.policy_id} requires {policy.approval_mode} approval."
        }
