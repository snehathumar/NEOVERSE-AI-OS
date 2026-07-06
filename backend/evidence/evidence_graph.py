class EvidenceGraph:
    """
    The central Evidence Graph that all intelligence modules consume.
    """
    def __init__(self):
        self.nodes = {}
        self.edges = []
        
        # Seed core AI nodes to make it a real graph
        self.add_node("decision_core", "Core", {"name": "Decision Engine"})
        self.add_node("parallel_sim", "Core", {"name": "Parallel Universe Simulator"})
        self.add_node("monitoring_ai", "Core", {"name": "Live Monitoring AI"})
        
        # Seed core edges
        self.add_edge("monitoring_ai", "decision_core", "feeds_alerts")
        self.add_edge("decision_core", "parallel_sim", "triggers_simulations")
        
    def add_node(self, node_id: str, node_type: str, data: dict):
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "data": data
        }
        
    def add_edge(self, from_id: str, to_id: str, relationship: str = "supports"):
        self.edges.append({
            "source": from_id, # using source and target for compatibility with streamlit_agraph
            "target": to_id,
            "relation": relationship
        })

    def get_graph(self) -> dict:
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges
        }

    def ingest_structured_evidence(self, evidence_dict: dict):
        """
        Takes output from Normalizer and creates a node in the graph.
        """
        node_id = f"evidence_{evidence_dict['source']}_{evidence_dict['timestamp']}"
        self.add_node(
            node_id=node_id,
            node_type="ExternalEvidence",
            data=evidence_dict
        )
        
        # Connect new evidence to the core monitoring system
        self.add_edge(node_id, "monitoring_ai", "ingested_by")
        self.add_edge(node_id, "decision_core", "influences")
        
        return node_id
