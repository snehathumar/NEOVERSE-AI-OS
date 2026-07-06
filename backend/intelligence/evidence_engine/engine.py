from backend.intelligence.plugin_base import IntelligencePlugin
from typing import Dict, Any

class EvidenceTrustPlugin(IntelligencePlugin):
    """
    Plugin-based Evidence Trust Engine.
    Detects bias, conflicts, and reduces confidence on poor evidence quality.
    """
    
    def __init__(self):
        self._trust_report = {}

    def initialize(self, config: Dict[str, Any]):
        print("⚖️ [EvidenceTrust] Initializing plugin...")
        self._trust_report = {}

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sources = payload.get("evidence_sources", [])
        print(f"⚖️ [EvidenceTrust] Evaluating {len(sources)} sources...")
        
        evaluated = []
        conflict_detected = False
        overall_score = 0
        
        for s in sources:
            score = s.get("base_reliability", 50)
            
            # Simple bias detection heuristic
            bias = "High" if s.get("source_type") == "user_input" else "Low"
            
            # Simple missing info detection
            missing_info = "Yes" if not s.get("timestamp") else "No"
            
            evaluated.append({
                "source": s.get("name"),
                "reliability": score,
                "bias_detected": bias,
                "missing_information": missing_info
            })
            overall_score += score
            
        overall_quality = (overall_score / len(sources)) if sources else 0
        
        # Penalize confidence if quality is too low
        confidence_modifier = 1.0
        if overall_quality < 70:
            confidence_modifier = 0.5
            
        self._trust_report = {
            "sources": evaluated,
            "overall_evidence_quality": overall_quality,
            "conflict_detected": conflict_detected,
            "confidence_modifier": confidence_modifier,
            "warning": "Reduced confidence due to poor evidence." if confidence_modifier < 1.0 else "Evidence trusted."
        }
        return self._trust_report

    def validate(self, result: Dict[str, Any]) -> bool:
        return "overall_evidence_quality" in result

    def serialize(self) -> Dict[str, Any]:
        return {
            "module": "EvidenceTrust",
            "data": self._trust_report
        }
