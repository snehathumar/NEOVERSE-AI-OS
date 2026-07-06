import json
import os
from backend.llm_client import generate_json

COMMUNITY_SCHEMA = {
    "type": "object",
    "properties": {
        "community_insights": {
            "type": "string",
            "description": "General summary of how similar businesses handled this decision."
        },
        "average_success_rate": {
            "type": "string",
            "description": "Percentage (e.g., '68%')"
        },
        "average_failure_rate": {
            "type": "string",
            "description": "Percentage (e.g., '32%')"
        },
        "most_common_strategy": {
            "type": "string"
        },
        "most_successful_decision": {
            "type": "string"
        },
        "source_type": {
            "type": "string",
            "enum": ["Community", "Historical", "AI Generated"],
            "description": "Strictly label where this insight came from."
        }
    },
    "required": [
        "community_insights", "average_success_rate", "average_failure_rate",
        "most_common_strategy", "most_successful_decision", "source_type"
    ]
}

class CommunityIntelligenceEngine:
    def __init__(self, data_file="backend/community_dataset.json"):
        """
        Designed with an abstraction layer. 
        Currently uses local JSON, but methods can easily be swapped for BigQuery clients.
        """
        self.data_file = data_file
        self.dataset = self._load_data()
        
    def _load_data(self):
        # MOCK BIGQUERY LOAD
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self._seed_dummy_data()
        
    def _seed_dummy_data(self):
        # A small anonymized dataset to bootstrap the community
        return [
            {"business_type": "Tech Startup", "business_size": "Small", "decision": "Increase Prices by 20%", "outcome": "Success", "profit_change": "+15%", "customer_change": "-5%", "confidence": 80},
            {"business_type": "Tech Startup", "business_size": "Small", "decision": "Aggressive Marketing Spend", "outcome": "Failure", "profit_change": "-30%", "customer_change": "+10%", "confidence": 40},
            {"business_type": "Retail", "business_size": "Medium", "decision": "Close physical stores", "outcome": "Success", "profit_change": "+25%", "customer_change": "0%", "confidence": 90},
            {"business_type": "Tech Startup", "business_size": "Medium", "decision": "Increase Prices by 20%", "outcome": "Success", "profit_change": "+10%", "customer_change": "-2%", "confidence": 85}
        ]

    def log_anonymized_decision(self, business_type: str, business_size: str, decision: str, outcome: str, profit_change: str, customer_change: str, confidence: int):
        """
        Logs an anonymized record. 
        TODO: Replace with BigQuery Insert in production.
        """
        record = {
            "business_type": business_type,
            "business_size": business_size,
            "decision": decision,
            "outcome": outcome,
            "profit_change": profit_change,
            "customer_change": customer_change,
            "confidence": confidence
        }
        self.dataset.append(record)
        
        with open(self.data_file, 'w') as f:
            json.dump(self.dataset, f, indent=4)

    def retrieve_similar_businesses(self, business_type: str, decision: str):
        """
        TODO: Replace with BigQuery SQL query (e.g. SELECT * WHERE business_type = x AND decision LIKE y)
        """
        # Simple local keyword matching for the mock
        similar = []
        for row in self.dataset:
            if row["business_type"].lower() == business_type.lower():
                similar.append(row)
        return similar

    def generate_community_insights(self, current_business: dict, decision: str):
        similar_records = self.retrieve_similar_businesses(current_business.get("industry", ""), decision)
        
        if not similar_records:
            # Fallback if no community data exists
            return {
                "community_insights": "No community data available for this exact scenario yet.",
                "average_success_rate": "N/A",
                "average_failure_rate": "N/A",
                "most_common_strategy": "N/A",
                "most_successful_decision": "N/A",
                "source_type": "AI Generated"
            }
            
        prompt = f"""
You are the Community Intelligence Module.
Current Business: {current_business}
Proposed Decision: "{decision}"

We have retrieved anonymized community data from similar businesses:
{json.dumps(similar_records, indent=2)}

Analyze this dataset.
Generate insights comparing the current business to the community.
Identify the Average Success, Average Failure, Most Common Strategy, and Most Successful Decision from the data.
Set 'source_type' to 'Community'.

Strictly return JSON matching the schema.
"""
        return generate_json(prompt, COMMUNITY_SCHEMA)
