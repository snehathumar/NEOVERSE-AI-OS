import abc
from typing import Dict, Any, List
from backend.simulation.models import UniverseOutcome
from backend.llm_client import generate_json

class BaseSimulator(abc.ABC):
    """
    Base interface for all Simulation Providers.
    """
    @abc.abstractmethod
    async def simulate_universe(self, 
                                scenario_name: str, 
                                time_horizon_months: int,
                                digital_twin_state: dict, 
                                decision_context: dict) -> UniverseOutcome:
        pass


class AIHeuristicSimulator(BaseSimulator):
    """
    Simulates outcomes using LLM heuristic reasoning to model variables, dependencies, and risks.
    """
    async def simulate_universe(self, 
                                scenario_name: str, 
                                time_horizon_months: int,
                                digital_twin_state: dict, 
                                decision_context: dict) -> UniverseOutcome:
        
        prompt = f"""
        You are the NEOVERSE AI Heuristic Simulator.
        Simulate the following business scenario over {time_horizon_months} months.
        
        Scenario Name: {scenario_name}
        
        Digital Twin Baseline:
        {digital_twin_state}
        
        Decision Implemented:
        {decision_context.get("recommendation", "Unknown decision")}
        
        Your task is to mathematically estimate (via heuristic reasoning) how this scenario and decision change the core variables (Revenue, Cost, Churn, Profit, etc.).
        Show the dependency chains (e.g. Marketing Spend -> Leads -> Sales -> Revenue).
        Calculate risk scores and uncertainty (confidence, data completeness, assumption quality).
        """
        
        schema = {
            "type": "object",
            "properties": {
                "variables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "starting_value": {"type": "number"},
                            "ending_value": {"type": "number"},
                            "percentage_change": {"type": "number"}
                        },
                        "required": ["name", "starting_value", "ending_value", "percentage_change"]
                    }
                },
                "dependencies_triggered": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_variable": {"type": "string"},
                            "target_variable": {"type": "string"},
                            "relationship_description": {"type": "string"},
                            "impact_multiplier": {"type": "number"}
                        },
                        "required": ["source_variable", "target_variable", "relationship_description", "impact_multiplier"]
                    }
                },
                "roi_estimate": {"type": "number"},
                "financial_risk_score": {"type": "integer"},
                "operational_risk_score": {"type": "integer"},
                "market_risk_score": {"type": "integer"},
                "confidence": {"type": "integer"},
                "data_completeness": {"type": "integer"},
                "assumption_quality": {"type": "integer"},
                "evidence_coverage": {"type": "integer"},
                "prediction_reliability": {"type": "integer"},
                "explanation": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": [
                "variables", "dependencies_triggered", "roi_estimate",
                "financial_risk_score", "operational_risk_score", "market_risk_score",
                "confidence", "data_completeness", "assumption_quality", 
                "evidence_coverage", "prediction_reliability", "explanation"
            ]
        }
        
        res = generate_json(prompt, schema)
        
        return UniverseOutcome(
            scenario_name=scenario_name,
            time_horizon_months=time_horizon_months,
            **res
        )
