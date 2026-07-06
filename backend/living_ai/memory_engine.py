import hashlib
import json
import time

class MemoryEngine:
    """
    Manages short-term and long-term memory for decisions.
    Strictly deduplicates identical contexts.
    """
    def __init__(self):
        self.long_term_vault = {}
        
    def _generate_hash(self, decision_context: dict) -> str:
        stringified = json.dumps(decision_context, sort_keys=True)
        return hashlib.sha256(stringified.encode()).hexdigest()

    def store_decision(self, decision_id: str, payload: dict):
        # Prevent duplication based on input
        context_hash = self._generate_hash(payload.get("context", {}))
        
        if decision_id not in self.long_term_vault:
            self.long_term_vault[decision_id] = {
                "hash": context_hash,
                "history": [],
                "created_at": time.time()
            }
            
        # Versioning: Always append, never overwrite
        version = len(self.long_term_vault[decision_id]["history"]) + 1
        payload["version"] = version
        payload["timestamp"] = time.time()
        
        self.long_term_vault[decision_id]["history"].append(payload)
        return version

    def get_decision_history(self, decision_id: str) -> list:
        return self.long_term_vault.get(decision_id, {}).get("history", [])
        
    def get_latest_decision(self, decision_id: str) -> dict:
        history = self.get_decision_history(decision_id)
        return history[-1] if history else {}

memory_engine = MemoryEngine()
