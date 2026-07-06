from typing import List, Dict, Any

class ExpertRegistry:
    """
    Manages the dynamic registration and selection of expert AI personas.
    """
    def __init__(self):
        self.experts = {}

    def register_expert(self, role: str, domains: List[str], focus: str):
        self.experts[role] = {
            "domains": domains,
            "focus": focus,
            "weight": 1.0 # Can be updated via historical analytics
        }

    def select_experts(self, decision_type: str) -> List[str]:
        """
        Dynamically select the expert panel based on the decision type.
        """
        panel = set()
        
        # Always include CEO for strategic oversight
        if "CEO" in self.experts:
            panel.add("CEO")
            
        for role, metadata in self.experts.items():
            if decision_type in metadata["domains"]:
                panel.add(role)
                
        # Limit to 5 experts maximum to prevent noise
        return list(panel)[:5]

registry = ExpertRegistry()
