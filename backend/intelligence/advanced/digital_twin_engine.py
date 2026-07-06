from backend.intelligence.advanced.models import BusinessTwinState
import json

class DigitalTwinEngine:
    """
    Maintains the AI clone of the user's business state.
    Used for safe, isolated experimentation.
    """
    def __init__(self):
        # In production, this would be loaded from Firestore based on the ContextEngine
        self._current_state = BusinessTwinState(
            revenue=5000000.0,
            profit=800000.0,
            demand=12000,
            inventory=5000,
            pricing=120.0,
            employees=45,
            customers=25000,
            marketing_budget=150000.0,
            competition_index=75,
            cash_flow=200000.0
        )
        self._simulation_snapshots = {}

    def get_current_state(self) -> dict:
        return self._current_state.dict()
        
    def clone_state(self) -> dict:
        """Returns an exact copy of the current state for simulation isolation."""
        return self._current_state.copy().dict()
        
    def save_simulation_snapshot(self, simulation_id: str, snapshot: dict):
        self._simulation_snapshots[simulation_id] = snapshot
        
    def get_simulation_snapshot(self, simulation_id: str) -> dict:
        return self._simulation_snapshots.get(simulation_id)

digital_twin_engine = DigitalTwinEngine()
