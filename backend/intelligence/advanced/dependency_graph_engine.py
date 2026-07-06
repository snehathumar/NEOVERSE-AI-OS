from backend.model_orchestrator.dynamic_models import generate_json
from backend.intelligence.advanced.models import DecisionGraph
import time

class DependencyGraphEngine:
    """
    Automatically discovers and maps the cascading relationships of any business decision.
    Builds a directed graph of primary, secondary, and long-term effects.
    """
    def build_dependency_graph(self, proposed_decision: str, business_context: dict) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "category": {"type": "string"}
                        },
                        "required": ["id", "label", "category"]
                    }
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "strength": {"type": "number"},
                            "description": {"type": "string"}
                        },
                        "required": ["source", "target", "strength", "description"]
                    }
                },
                "critical_nodes": {"type": "array", "items": {"type": "string"}},
                "cascading_effects": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["nodes", "edges", "critical_nodes", "cascading_effects"]
        }
        
        prompt = f"""
        Analyze the cascading effects of the following decision on the business.
        Decision: {proposed_decision}
        Business Context: {business_context}
        
        Generate a strict directed graph (nodes and edges). 
        Edges must have a strength between 0.0 and 1.0 indicating how strongly the source affects the target.
        Identify critical bottleneck nodes and list the cascading long-term effects.
        """
        
        print(f"🕸️ [DependencyGraphEngine] Mapping cascading effects for: '{proposed_decision}'")
        raw_result = generate_json(prompt, schema)
        
        # We can validate it with Pydantic if needed, but returning dict for easy serialization
        return raw_result

dependency_graph_engine = DependencyGraphEngine()
