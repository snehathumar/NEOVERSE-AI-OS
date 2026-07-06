from backend.intelligence.advanced.digital_twin_engine import digital_twin_engine
import uuid

class SimulationLab:
    """
    The safe experimentation environment. 
    Applies user-defined parameter changes to the Digital Twin and calculates deltas.
    """
    
    def apply_scenario(self, parameters_delta: dict) -> dict:
        """
        Applies changes (e.g., {"pricing": "+10%", "marketing_budget": "-5000"})
        and runs a simulated calculation to determine the 'After' state.
        """
        print(f"🧪 [SimulationLab] Running safe experiment on Digital Twin...")
        
        sim_id = str(uuid.uuid4())
        before_state = digital_twin_engine.clone_state()
        after_state = digital_twin_engine.clone_state()
        
        # Example Simulation Logic (In production, this triggers the LLM/Parallel Universe Engine)
        if "pricing" in parameters_delta:
            new_price = parameters_delta["pricing"]
            after_state["pricing"] = new_price
            
            # Simple elastic demand model: price goes up, demand goes down
            price_change_ratio = new_price / before_state["pricing"]
            after_state["demand"] = int(before_state["demand"] * (2 - price_change_ratio))
            after_state["revenue"] = after_state["demand"] * after_state["pricing"]
            
        if "marketing_budget" in parameters_delta:
            new_marketing = parameters_delta["marketing_budget"]
            after_state["marketing_budget"] = new_marketing
            
            # More marketing = more customers
            marketing_ratio = new_marketing / before_state["marketing_budget"]
            after_state["customers"] = int(before_state["customers"] * (0.8 + (0.2 * marketing_ratio)))
            
        # Calculate Delta
        delta = {}
        for key in before_state.keys():
            diff = after_state[key] - before_state[key]
            delta[key] = diff
            
        result = {
            "simulation_id": sim_id,
            "state_before": before_state,
            "state_after": after_state,
            "delta": delta
        }
        
        # Save snapshot
        digital_twin_engine.save_simulation_snapshot(sim_id, result)
        
        return result

simulation_lab = SimulationLab()
