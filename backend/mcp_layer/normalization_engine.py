import time

class StructuredEvidence:
    """
    Standard format for all API data passing into the Decision Intelligence Engine.
    """
    def __init__(self, source_tool: str, raw_data: dict, confidence: int = 100):
        self.source_tool = source_tool
        self.timestamp = time.time()
        self.confidence_score = confidence
        
        # If the API failed, we structure it gracefully
        if "error" in raw_data:
            self.status = "FALLBACK"
            self.data = raw_data.get("fallback_data", {})
            self.confidence_score = 30 # Lower confidence for fallback data
        else:
            self.status = "LIVE"
            self.data = raw_data

    def to_dict(self):
        return {
            "source": self.source_tool,
            "status": self.status,
            "timestamp": self.timestamp,
            "confidence": self.confidence_score,
            "data": self.data
        }


class NormalizationEngine:
    """
    Converts raw tool output into StructuredEvidence.
    """
    def normalize(self, tool_name: str, raw_response: dict) -> StructuredEvidence:
        print(f"🧩 [Normalization] Coercing '{tool_name}' payload into StructuredEvidence.")
        # In a real app, you might have tool-specific normalization logic here.
        # For the MVP, we just wrap it into the standard envelope.
        evidence = StructuredEvidence(tool_name, raw_response)
        return evidence

normalization_engine = NormalizationEngine()
