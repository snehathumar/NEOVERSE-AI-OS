class LookerDataModels:
    """
    Looker Ready Data Models.
    Provides standard JSON/SQL schemas optimized for Business Intelligence dashboards.
    """
    @staticmethod
    def get_decision_analytics_view() -> dict:
        return {
            "view_name": "decision_analytics",
            "schema": {
                "decision_id": "STRING",
                "timestamp": "TIMESTAMP",
                "intent_type": "STRING",
                "confidence_score": "FLOAT",
                "simulated_revenue_impact": "FLOAT",
                "success_flag": "BOOLEAN"
            }
        }
        
    @staticmethod
    def get_community_intelligence_view() -> dict:
        return {
            "view_name": "community_intelligence_aggregates",
            "schema": {
                "industry": "STRING",
                "average_risk_score": "FLOAT",
                "common_strategy": "STRING"
            }
        }
