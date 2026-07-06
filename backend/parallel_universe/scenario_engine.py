from backend.model_orchestrator.dynamic_models import generate_json
from backend.parallel_universe.models import UniverseScenario

class ScenarioEngine:
    """
    Generates distinct baseline universes by consuming the Evidence Graph.
    No generic templates. Completely driven by structured evidence.
    """
    async def generate_baseline_scenarios(self, evidence_graph: dict, decision_context: str) -> list[dict]:
        schema = {
            "type": "object",
            "properties": {
                "scenarios": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "universe_type": {"type": "string", "enum": ["Best Case", "Most Probable", "Conservative", "Worst Case", "Dynamic Alternative"]},
                            "summary": {"type": "string"},
                            "driving_evidence_ids": {"type": "array", "items": {"type": "string"}},
                            "assumptions_made": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["universe_type", "summary", "driving_evidence_ids", "assumptions_made"]
                    }
                }
            },
            "required": ["scenarios"]
        }
        
        prompt = f"""
        Given the following Evidence Graph and Decision Context, generate 5 distinct baseline scenarios.
        Rules:
        - Best Case: Assume 90% of favorable assumptions hold true.
        - Most Probable: Weight outcomes based on evidence strength.
        - Conservative: Penalize assumptions lacking external API validation.
        - Worst Case: Simulate top 3 risks coming true.
        - Dynamic Alternative: A wild-card strategy based on the data.
        
        Decision Context: {decision_context}
        Evidence Graph Nodes: {evidence_graph.get('nodes', [])}
        """
        
        result = generate_json(prompt, schema)
        return result.get("scenarios", [])

scenario_engine = ScenarioEngine()
