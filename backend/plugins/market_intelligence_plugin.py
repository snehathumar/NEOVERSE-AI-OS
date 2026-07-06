import uuid
from datetime import datetime, timezone
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus
from backend.llm_client import generate_json

MARKET_INTELLIGENCE_SCHEMA = {
    "type": "object",
    "properties": {
        "market_trends": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Macro trends currently affecting the business sector."
        },
        "seasonality": {
            "type": "string",
            "description": "Impact of current seasonality (e.g. holiday season, summer slump)."
        },
        "competition": {
            "type": "string",
            "description": "Recent competitor movements or threats."
        },
        "demand_changes": {
            "type": "string",
            "description": "Shifts in consumer demand or purchasing power."
        },
        "opportunity_signals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Actionable signals based on the market conditions."
        }
    },
    "required": [
        "market_trends", "seasonality", "competition", 
        "demand_changes", "opportunity_signals"
    ]
}

class MarketIntelligencePlugin(NeoversePlugin):
    """
    Market Intelligence Engine.
    Periodically (or event-driven) scans for Market Trends, Seasonality, Competition, 
    and Demand Changes, generating Opportunity Signals.
    Stores findings via EventBus which routes to BigQuery.
    """
    def initialize(self):
        # Could subscribe to a daily heartbeat event, but for now we expose a direct trigger
        event_bus.subscribe("TriggerMarketAnalysis", self.analyze_market)

    def analyze_market(self, payload: dict):
        """
        Analyzes the market for a specific business context and generates intelligence.
        """
        business_type = payload.get("business_type", "General Business")
        market_context = payload.get("market_context", "Normal Conditions")
        
        prompt = f"""
You are the Market Intelligence Engine.
Analyze the current market landscape for a {business_type} operating in {market_context}.

Identify:
1. Market Trends
2. Seasonality effects
3. Competition
4. Demand Changes

Based on these findings, generate actionable Opportunity Signals.
Return strictly JSON matching the schema.
"""
        try:
            result = generate_json(prompt, MARKET_INTELLIGENCE_SCHEMA)
            
            # Package into a structured log
            log_entry = {
                "market_log_id": str(uuid.uuid4()),
                "business_type": business_type,
                "trends": result.get("market_trends"),
                "seasonality": result.get("seasonality"),
                "competition": result.get("competition"),
                "demand_changes": result.get("demand_changes"),
                "opportunity_signals": result.get("opportunity_signals"),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Publish to EventBus so Analytics Plugin can store it in BigQuery
            event_bus.publish("MarketIntelligenceGenerated", log_entry)
            
            # Opportunity Service could also listen to this event
            print(f"📈 [Market Intelligence] Generated {len(result.get('opportunity_signals', []))} Opportunity Signals.")
            
        except Exception as e:
            print(f"[Market Intelligence Engine] Failed to analyze market: {e}")

