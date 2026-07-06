import json
import uuid
from datetime import datetime, timezone
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus
from backend.llm_client import generate_json
from backend.analytics_service import analytics_service

COMMUNITY_SCHEMA = {
    "type": "object",
    "properties": {
        "businesses_similar_to_yours": {
            "type": "integer",
            "description": "Count of similar businesses analyzed."
        },
        "average_revenue_growth": {
            "type": "string",
            "description": "E.g., '+12%'"
        },
        "common_mistakes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Mistakes similar businesses made in this scenario."
        },
        "successful_strategies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Strategies that led to success for similar businesses."
        }
    },
    "required": [
        "businesses_similar_to_yours", "average_revenue_growth", 
        "common_mistakes", "successful_strategies"
    ]
}

class CommunityIntelligencePlugin(NeoversePlugin):
    """
    Community Intelligence Engine.
    Analyzes anonymized businesses to generate community statistics.
    Stores analytics inside BigQuery. Supports simulated data for hackathons.
    Never exposes personal data.
    """
    def initialize(self):
        # Listen for completed decisions to anonymize and store them in the community pool
        event_bus.subscribe("DecisionCreated", self.anonymize_and_store_decision)

    def anonymize_and_store_decision(self, payload: dict):
        """
        Strips all PII (Personal Identifiable Information) and stores the decision
        as an anonymized community data point in BigQuery.
        """
        # Anonymization process (strip user_id, exact names, etc.)
        anonymized_record = {
            "community_id": str(uuid.uuid4()),
            "business_type": payload.get("business_type", "Unknown"),
            "decision_query": payload.get("decision_query", ""),
            "confidence_score": payload.get("confidence_score", 0),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in BigQuery via Analytics Service
        try:
            # We assume analytics_service has a table for this, or we log it generically
            # For hackathon, we push this to an event bus or use existing BQ logic
            event_bus.publish("CommunityDataLogged", anonymized_record)
            # In a real GCP setup, this writes to `community_analytics` dataset
        except Exception as e:
            print(f"[Community Engine] Failed to store anonymized record: {e}")

    def _get_simulated_hackathon_data(self, business_type: str) -> list:
        """
        Returns simulated hackathon data for comparisons.
        """
        return [
            {"business_type": business_type, "outcome": "Success", "revenue_growth": "+15%", "mistake": "Scaled too fast", "strategy": "Focus on retention"},
            {"business_type": business_type, "outcome": "Failure", "revenue_growth": "-5%", "mistake": "Ignored customer feedback", "strategy": "N/A"},
            {"business_type": business_type, "outcome": "Success", "revenue_growth": "+20%", "mistake": "Underpriced product", "strategy": "Aggressive marketing"}
        ]

    def generate_community_statistics(self, business_type: str, decision_query: str) -> dict:
        """
        Analyzes the community dataset (BigQuery or Simulated) to generate insights.
        """
        # 1. Fetch data from BigQuery (simulated for hackathon)
        community_data = self._get_simulated_hackathon_data(business_type)
        
        prompt = f"""
You are the Community Intelligence Engine.
Analyze the following anonymized community data for businesses similar to the current user's.
The user is a "{business_type}" considering: "{decision_query}".

Anonymized Community Data:
{json.dumps(community_data, indent=2)}

Generate statistics:
1. Count of businesses similar to yours in this dataset.
2. Average Revenue Growth.
3. Common Mistakes.
4. Successful Strategies.

Never expose personal data.
Return strictly JSON matching the schema.
"""
        try:
            return generate_json(prompt, COMMUNITY_SCHEMA)
        except Exception as e:
            print(f"[Community Engine] Error: {e}")
            return {
                "businesses_similar_to_yours": 0,
                "average_revenue_growth": "N/A",
                "common_mistakes": ["Failed to load community data"],
                "successful_strategies": []
            }
