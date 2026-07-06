import uuid
from typing import Dict, Any, List
from backend.execution.models import ExecutionPlan, TaskNode
from backend.llm_client import generate_json

class ExecutionPlanner:
    """
    Translates a high-level strategic recommendation into a concrete DAG of executable tasks.
    """
    def generate_plan(self, recommendation: str, decision_context: dict) -> ExecutionPlan:
        prompt = f"""
        You are the NEOVERSE Execution Planner.
        Convert the following high-level recommendation into a strict Directed Acyclic Graph (DAG) of executable tasks.
        
        Recommendation: {recommendation}
        Context: {decision_context}
        
        Available Plugins: ['RestAPIPlugin', 'MCPPlugin']
        
        Create a list of sequential or parallel tasks. Each task must have a unique ID, dependencies (if any), and inputs.
        Ensure every action is safe, idempotent, and capable of rollback.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string"},
                            "plugin_name": {"type": "string", "enum": ["RestAPIPlugin", "MCPPlugin"]},
                            "action_name": {"type": "string"},
                            "dependencies": {"type": "array", "items": {"type": "string"}},
                            "inputs": {"type": "object"},
                            "rollback_steps": {"type": "object"}
                        },
                        "required": ["task_id", "plugin_name", "action_name", "dependencies", "inputs"]
                    }
                },
                "priority": {"type": "string"},
                "risk_level": {"type": "string"},
                "success_criteria": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["goal", "tasks", "priority", "risk_level", "success_criteria"]
        }
        
        res = generate_json(prompt, schema)
        
        tasks = []
        for t in res.get("tasks", []):
            tasks.append(TaskNode(**t))
            
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            goal=res.get("goal", "Execute Decision"),
            tasks=tasks,
            priority=res.get("priority", "Normal"),
            owner="NEOVERSE_EXECUTION_ENGINE",
            estimated_duration_ms=60000,
            risk_level=res.get("risk_level", "Medium"),
            success_criteria=res.get("success_criteria", [])
        )
