import time
import json

class StructuredEvidence:
    """
    The normalized enterprise schema for all Evidence.
    No raw API responses should ever reach the AI.
    """
    def __init__(
        self, 
        source: str, 
        raw_data: dict, 
        category: str = "General", 
        confidence: int = 100
    ):
        self.source = source
        self.timestamp = time.time()
        self.freshness = "Live"
        self.reliability = "High"
        self.category = category
        self.confidence = confidence
        
        # Fallback check
        if "error" in raw_data:
            self.reliability = "Low"
            self.freshness = "Historical/Simulated"
            self.confidence = 30
            self.structured_data = raw_data.get("fallback_data", {})
            self.summary = f"Failed to reach API. {raw_data.get('error')}"
        else:
            self.structured_data = raw_data
            self.summary = f"Live data from {source} API."

        self.metadata = {
            "processed_at": time.time(),
            "schema_version": "1.0"
        }

    def to_dict(self):
        return {
            "source": self.source,
            "timestamp": self.timestamp,
            "freshness": self.freshness,
            "reliability": self.reliability,
            "confidence": self.confidence,
            "category": self.category,
            "summary": self.summary,
            "structured_data": self.structured_data,
            "metadata": self.metadata
        }

class Normalizer:
    """
    Converts raw tool output into the StructuredEvidence format.
    """
    def normalize(self, tool_name: str, raw_response: dict, category: str = "General") -> dict:
        print(f"🧩 [Normalizer] Standardizing '{tool_name}' payload into Evidence Schema.")
        evidence = StructuredEvidence(tool_name, raw_response, category)
        return evidence.to_dict()

normalizer = Normalizer()
