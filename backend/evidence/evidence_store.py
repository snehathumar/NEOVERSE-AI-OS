from backend.evidence.evidence_graph import EvidenceGraph

class EvidenceStore:
    """
    Manages active Evidence Graphs for current decision sessions.
    """
    def __init__(self):
        self._active_graphs = {}
        
    def get_or_create_graph(self, session_id: str) -> EvidenceGraph:
        if session_id not in self._active_graphs:
            self._active_graphs[session_id] = EvidenceGraph()
        return self._active_graphs[session_id]

evidence_store = EvidenceStore()
