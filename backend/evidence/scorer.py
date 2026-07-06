from backend.evidence.models import EvidenceItem

class TrustScorer:
    """
    Calculates the final Trust Score for an evidence item.
    """
    def calculate_trust(self, raw_evidence: dict, bias_score: int, freshness: str, source_reputation: int) -> int:
        """
        Dynamically calculates Trust Score based on:
        - Source Reputation (40%)
        - Bias Score penalty (30%)
        - Freshness penalty (30%)
        """
        base_score = source_reputation * 0.40
        
        # Bias Penalty (higher bias = lower trust)
        bias_factor = (100 - bias_score) * 0.30
        
        # Freshness Penalty
        freshness_multipliers = {
            "Real-Time": 1.0,
            "Recent": 0.95,
            "Current": 0.80,
            "Historical": 0.50,
            "Outdated": 0.20
        }
        freshness_factor = 100 * freshness_multipliers.get(freshness, 0.5) * 0.30
        
        final_score = int(base_score + bias_factor + freshness_factor)
        
        # Ensure bounds
        return max(0, min(100, final_score))
