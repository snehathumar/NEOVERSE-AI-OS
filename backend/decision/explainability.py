from typing import Dict, Any, List
from backend.llm_client import generate_json
from backend.decision.models import DependencyGraph, DependencyNode, DependencyEdge

EXPLAINABILITY_SCHEMA = {
    "type": "object",
    "properties": {
        "explainable_ai": {
            "type": "object",
            "properties": {
                "why_this_recommendation": {"type": "string"},
                "why_not_alternatives": {"type": "string"},
                "key_evidence_influence": {"type": "string"},
                "key_assumptions": {"type": "string"},
                "unresolved_risks": {"type": "string"}
            },
            "required": ["why_this_recommendation", "why_not_alternatives", "key_evidence_influence", "key_assumptions", "unresolved_risks"]
        },
        "dependency_graph": {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "type": {"type": "string"}
                        },
                        "required": ["id", "label", "type"]
                    }
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "impact_level": {"type": "string"}
                        },
                        "required": ["source", "target", "impact_level"]
                    }
                }
            },
            "required": ["nodes", "edges"]
        },
        "executive_summary": {"type": "string"},
        "next_actions": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["explainable_ai", "dependency_graph", "executive_summary", "next_actions"]
}

class ExplainabilityEngine:
    """
    Step 22: Explainable AI Generation and Dependency Graph.
    """
    def execute(self, recommendation: str, problem: dict, alternatives: List[str]) -> Dict[str, Any]:
        prompt = f"""
        You are the NEOVERSE Explainability Engine.
        Generate transparent explanations for this decision.
        
        Recommended Strategy: {recommendation}
        Rejected Alternatives: {alternatives}
        Problem: {problem}
        
        1. Write a clear Executive Summary.
        2. Generate the Explainable AI (Why this? Why not alternatives? What evidence/assumptions mattered?).
        3. Generate Next Actions.
        4. Construct a Dependency Graph (Nodes and Edges showing cause, effect, and dependencies of this decision).
        """
        res = generate_json(prompt, EXPLAINABILITY_SCHEMA)
        
        return {
            "explainable_ai": res.get("explainable_ai", {}),
            "executive_summary": res.get("executive_summary", ""),
            "next_actions": res.get("next_actions", []),
            "dependency_graph": DependencyGraph(**res.get("dependency_graph", {}))
        }
