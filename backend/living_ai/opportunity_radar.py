from backend.model_orchestrator.dynamic_models import generate_json
import time

class OpportunityRadar:
    """
    Proactively discovers hidden opportunities (Revenue Growth, Cost Reduction, etc.)
    without waiting for the user to ask.
    """
    def scan_for_opportunities(self, evidence_graph_data: dict, business_context: dict) -> list:
        schema = {
            "type": "object",
            "properties": {
                "opportunities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "enum": ["Revenue Growth", "Cost Reduction", "Operational Efficiency", "Marketing", "Expansion", "Automation", "Customer Retention", "Risk Reduction"]},
                            "expected_benefit": {"type": "string"},
                            "difficulty": {"type": "string", "enum": ["Low", "Medium", "High"]},
                            "confidence": {"type": "integer"},
                            "required_actions": {"type": "array", "items": {"type": "string"}},
                            "time_horizon": {"type": "string"}
                        },
                        "required": ["category", "expected_benefit", "difficulty", "confidence", "required_actions", "time_horizon"]
                    }
                }
            },
            "required": ["opportunities"]
        }
        
        prompt = f"""
        Proactively scan the Evidence Graph and Business Context for hidden opportunities.
        Business Context: {business_context}
        Evidence: {evidence_graph_data}
        """
        
        print(f"✨ [Opportunity Radar] Scanning for proactive opportunities...")
        res = generate_json(prompt, schema)
        
        # Add generation timestamp
        opps = res.get("opportunities", [])
        for opp in opps:
            opp["discovered_at"] = time.time()
            
        return opps

opportunity_radar = OpportunityRadar()
