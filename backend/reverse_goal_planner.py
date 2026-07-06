import json
from backend.llm_client import generate_json

REVERSE_GOAL_SCHEMA = {
    "type": "object",
    "properties": {
        "target": {"type": "string"},
        "revenue_required": {"type": "string"},
        "customers_needed": {"type": "string"},
        "sales_volume_needed": {"type": "string"},
        "marketing_budget_and_strategy": {"type": "string"},
        "inventory_and_operations": {"type": "string"},
        "todays_actions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Immediate tasks to start executing today."
        },
        "milestones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timeframe": {"type": "string"},
                    "metric": {"type": "string"}
                },
                "required": ["timeframe", "metric"]
            },
            "description": "Key milestones tracking backwards from the goal."
        }
    },
    "required": [
        "target", "revenue_required", "customers_needed", 
        "sales_volume_needed", "marketing_budget_and_strategy", 
        "inventory_and_operations", "todays_actions", "milestones"
    ]
}

class ReverseGoalPlanner:
    """
    Independent engine that works backwards from a stated goal.
    Helps users figure out exactly what actions they need to take today to reach a long-term target.
    """
    def __init__(self):
        pass

    def plan_backwards(self, target_goal: str, business_context: str) -> dict:
        prompt = f"""
You are the Reverse Goal Planner.
The user wants to reach a specific target. You must work backwards from that target down to what they need to do TODAY.

Target Goal: "{target_goal}"
Business Context: "{business_context}"

Work strictly backwards through this pipeline:
1. Target
2. Revenue Required
3. Customers Needed
4. Sales Volume Needed
5. Marketing Budget & Strategy
6. Inventory & Operations
7. Today's Actions

Also generate key milestones (timeframes and metrics) to track progress.

Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, REVERSE_GOAL_SCHEMA)
        except Exception as e:
            return {
                "target": target_goal,
                "revenue_required": "Error calculating",
                "customers_needed": "Error calculating",
                "sales_volume_needed": "Error calculating",
                "marketing_budget_and_strategy": "Error calculating",
                "inventory_and_operations": "Error calculating",
                "todays_actions": [f"Failed to generate plan: {str(e)}"],
                "milestones": []
            }

# Singleton instance
reverse_goal_planner = ReverseGoalPlanner()
