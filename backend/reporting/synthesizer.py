from typing import Dict, Any
from backend.llm_client import generate_json
from backend.reporting.models import ExplainabilityAudit

class ReportSynthesizer:
    """
    Synthesizes the raw pipeline outputs into a cohesive Executive Report narrative.
    """
    def synthesize_narrative(self, 
                             evidence_data: dict, 
                             decision_data: dict, 
                             debate_data: dict, 
                             simulation_data: dict) -> Dict[str, Any]:
                             
        prompt = f"""
        You are the NEOVERSE Executive Report Synthesizer.
        Take the structured outputs from the core pipeline and write the narrative sections for an enterprise-grade Executive Report.
        
        Evidence Output: {evidence_data}
        Decision Output: {decision_data}
        Debate Output: {debate_data}
        Simulation Output: {simulation_data}
        
        Write cohesive, professional executive summaries for each section.
        Generate a detailed Explainability Audit explaining why this recommendation won, what evidence drove it, and how experts and simulations influenced it.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "executive_summary": {"type": "string"},
                "business_context": {"type": "string"},
                "verified_evidence_summary": {"type": "string"},
                "key_assumptions": {"type": "string"},
                "decision_analysis": {"type": "string"},
                "expert_debate_summary": {"type": "string"},
                "simulation_summary": {"type": "string"},
                "risk_assessment": {"type": "string"},
                "opportunity_assessment": {"type": "string"},
                "financial_impact": {"type": "string"},
                "kpi_forecast_summary": {"type": "string"},
                "recommended_action_plan": {"type": "string"},
                "explainability": {
                    "type": "object",
                    "properties": {
                        "why_this_recommendation": {"type": "string"},
                        "why_not_alternatives": {"type": "string"},
                        "key_evidence_influence": {"type": "array", "items": {"type": "string"}},
                        "key_assumptions_made": {"type": "array", "items": {"type": "string"}},
                        "expert_opinion_shifts": {"type": "array", "items": {"type": "string"}},
                        "simulation_driving_factor": {"type": "string"},
                        "remaining_uncertainties": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["why_this_recommendation", "why_not_alternatives", "key_evidence_influence", 
                                 "key_assumptions_made", "expert_opinion_shifts", "simulation_driving_factor", 
                                 "remaining_uncertainties"]
                }
            },
            "required": [
                "executive_summary", "business_context", "verified_evidence_summary", "key_assumptions",
                "decision_analysis", "expert_debate_summary", "simulation_summary", "risk_assessment",
                "opportunity_assessment", "financial_impact", "kpi_forecast_summary", "recommended_action_plan",
                "explainability"
            ]
        }
        
        return generate_json(prompt, schema)
