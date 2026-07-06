from backend.intelligence.advanced.models import EvidenceTrustMatrix

class EvidenceTrustEngine:
    """
    Evaluates evidence quality before making decisions.
    Assigns reliability, freshness, and weight to prevent the AI from trusting bad data.
    """
    
    # Hardcoded baseline trust scores for MVP. 
    # In production, these would be dynamically calculated based on historical accuracy.
    TRUST_BASELINES = {
        "Weather API": {"reliability": 98, "weight": 1.0},
        "Finance API": {"reliability": 99, "weight": 1.2},
        "Traffic API": {"reliability": 90, "weight": 0.8},
        "News API": {"reliability": 71, "weight": 0.6},
        "Business Trends": {"reliability": 92, "weight": 1.1},
        "Internal Sales": {"reliability": 95, "weight": 1.0},
        "User Guess": {"reliability": 35, "weight": 0.2},
        "Old Spreadsheet": {"reliability": 58, "weight": 0.4}
    }

    def evaluate_evidence(self, evidence_sources: list) -> dict:
        print(f"⚖️ [EvidenceTrustEngine] Evaluating trust for {len(evidence_sources)} sources...")
        
        sources_scored = []
        total_weight = 0
        weighted_score_sum = 0
        warnings = []
        
        for source in evidence_sources:
            source_name = source.get("source_name", "Unknown")
            is_live = source.get("is_live", False)
            
            baseline = self.TRUST_BASELINES.get(source_name, {"reliability": 50, "weight": 0.5})
            
            rel_score = baseline["reliability"]
            freshness = 100 if is_live else 40
            
            # Penalize old data
            confidence_contrib = int((rel_score * 0.7) + (freshness * 0.3))
            
            if confidence_contrib < 60:
                warnings.append(f"Weak Evidence Warning: '{source_name}' has low reliability/freshness. Proceed with caution.")
                
            sources_scored.append({
                "source_name": source_name,
                "reliability_score": rel_score,
                "freshness_score": freshness,
                "confidence_contribution": confidence_contrib,
                "weight": baseline["weight"]
            })
            
            total_weight += baseline["weight"]
            weighted_score_sum += (confidence_contrib * baseline["weight"])
            
        overall = int(weighted_score_sum / total_weight) if total_weight > 0 else 0
        
        return {
            "sources": sources_scored,
            "overall_trust_score": overall,
            "weak_evidence_warnings": warnings
        }

evidence_trust_engine = EvidenceTrustEngine()
