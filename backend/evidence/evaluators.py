from backend.llm_client import generate_json
from backend.evidence.models import BiasReport
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

class EvidenceEvaluator:
    """
    Evaluates raw evidence for bias, freshness, and contradictions.
    """
    
    def evaluate_bias(self, content: str, source: str) -> BiasReport:
        prompt = f"""
        You are the NEOVERSE Bias Detector.
        Evaluate the following evidence for bias.
        Source: {source}
        Content: {content}
        
        Score source bias, temporal bias, and confirmation bias from 0-100 (where 100 is extremely biased).
        Provide an overall bias score and explanation.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "source_bias": {"type": "integer"},
                "temporal_bias": {"type": "integer"},
                "confirmation_bias": {"type": "integer"},
                "overall_bias_score": {"type": "integer"},
                "explanation": {"type": "string"}
            },
            "required": ["source_bias", "temporal_bias", "confirmation_bias", "overall_bias_score", "explanation"]
        }
        
        res = generate_json(prompt, schema)
        return BiasReport(**res)

    def determine_freshness(self, timestamp_str: str, domain_policy: dict) -> str:
        """
        Calculates freshness based on the domain policy (e.g., Tech = 1 year is Outdated, History = 50 years is Current).
        Returns: Real-Time, Recent, Current, Historical, Outdated.
        """
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - timestamp).days
            
            # Use domain policy thresholds, fallback to defaults
            outdated_threshold = domain_policy.get("outdated_days", 365*2)
            historical_threshold = domain_policy.get("historical_days", 365)
            recent_threshold = domain_policy.get("recent_days", 30)
            
            if age_days > outdated_threshold:
                return "Outdated"
            elif age_days > historical_threshold:
                return "Historical"
            elif age_days > recent_threshold:
                return "Current"
            elif age_days > 1:
                return "Recent"
            else:
                return "Real-Time"
                
        except Exception:
            return "Current" # Default if parsing fails

    def detect_contradictions(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans aggregated evidence to find conflicting claims/statistics.
        Returns a list of raw conflict reports.
        """
        if len(evidence_list) < 2:
            return []
            
        prompt = f"""
        You are the NEOVERSE Contradiction Detector.
        Review the following collected evidence items.
        
        Evidence:
        {[e for e in evidence_list]}
        
        Identify any explicit contradictions (e.g. conflicting financial numbers, opposing claims).
        If contradictions exist, output a list of them. If none exist, output an empty list.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "conflicts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "conflicting_sources": {"type": "array", "items": {"type": "string"}},
                            "possible_reasons_for_conflict": {"type": "string"},
                            "recommended_resolution": {"type": "string"},
                            "additional_evidence_required": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["conflicting_sources", "possible_reasons_for_conflict", "recommended_resolution", "additional_evidence_required"]
                    }
                }
            },
            "required": ["conflicts"]
        }
        
        res = generate_json(prompt, schema)
        return res.get("conflicts", [])
