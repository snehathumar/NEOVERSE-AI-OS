from typing import List, Tuple
from backend.evidence.models import KnowledgeGraphNode, KnowledgeGraphEdge, EvidenceItem
from backend.llm_client import generate_json

class EvidenceGraphBuilder:
    """
    Builds the structured Knowledge Graph and Dependency Graph from verified evidence.
    """
    
    def build_graph(self, evidence: List[EvidenceItem], context: dict) -> Tuple[List[KnowledgeGraphNode], List[KnowledgeGraphEdge]]:
        prompt = f"""
        You are the NEOVERSE Evidence Graph Builder.
        Analyze the collected evidence and the business context to construct a Knowledge Graph.
        
        Evidence: {[e.model_dump() for e in evidence]}
        Context: {context}
        
        Extract the core claims, assumptions, and link them to the evidence.
        Relationships should be: supports, contradicts, derives_from, infers.
        """
        
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
                            "type": {"type": "string"},
                            "properties": {"type": "object", "additionalProperties": {"type": "string"}}
                        },
                        "required": ["id", "label", "type", "properties"]
                    }
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "relationship": {"type": "string"}
                        },
                        "required": ["source", "target", "relationship"]
                    }
                }
            },
            "required": ["nodes", "edges"]
        }
        
        res = generate_json(prompt, schema)
        
        nodes = [KnowledgeGraphNode(**n) for n in res.get("nodes", [])]
        edges = [KnowledgeGraphEdge(**e) for e in res.get("edges", [])]
        
        return nodes, edges
