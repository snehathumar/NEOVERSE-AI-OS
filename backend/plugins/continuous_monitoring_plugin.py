import uuid
import json
from datetime import datetime, timezone
from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus
from backend.monitoring_service import monitoring_engine, MonitoringPluginBase
from backend.api_tool_manager import api_tool_manager
from backend.llm_client import generate_json

MONITORING_EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "change_detected": {
            "type": "boolean",
            "description": "True if the new data significantly changes the environment of the original decision."
        },
        "recalculated_recommendation": {
            "type": "string",
            "description": "The updated recommendation based on the new data."
        },
        "new_confidence": {
            "type": "integer",
            "description": "Updated confidence score (0-100) after factoring in the new data."
        },
        "alert_message": {
            "type": "string",
            "description": "A concise alert message detailing what changed."
        }
    },
    "required": ["change_detected", "recalculated_recommendation", "new_confidence", "alert_message"]
}

class ContinuousMonitoringJob:
    """
    Represents an active monitoring job for a specific decision.
    Uses APIToolManager to scan live external environments.
    """
    def __init__(self, decision_id: str, business_type: str, decision_query: str, location="New York", keyword="Retail"):
        self.job_id = str(uuid.uuid4())
        self.decision_id = decision_id
        self.business_type = business_type
        self.decision_query = decision_query
        self.location = location
        self.keyword = keyword
        self.last_evaluation = None
        
    def check_for_changes(self) -> list:
        """
        Polls APIToolManager across Weather, Market, News, and Business KPIs.
        Evaluates the data via LLM to detect critical changes.
        """
        # Fetch live/fallback data
        weather_data = api_tool_manager.get_weather(self.location)
        news_data = api_tool_manager.get_news(self.keyword)
        market_data = api_tool_manager.get_business_trends(self.keyword)
        
        # Simulate Business KPIs (in reality, fetched from internal DB/Stripe API)
        kpi_data = {"status": "success", "data": {"revenue_trend": "Stable", "foot_traffic": "Down 5%"}}
        
        prompt = f"""
You are the Continuous Monitoring Engine.
Original Business Decision: "{self.decision_query}"

New Monitoring Data Detected:
- Weather: {json.dumps(weather_data.get("data", {}))}
- News: {json.dumps(news_data.get("data", {}))}
- Market Trends: {json.dumps(market_data.get("data", {}))}
- Business KPIs: {json.dumps(kpi_data.get("data", {}))}

Evaluate if these environmental changes require a change in strategy.
If yes, set 'change_detected' to true, generate an 'alert_message', provide a 'recalculated_recommendation', and calculate the 'new_confidence'.

Return strictly JSON matching the schema.
"""
        events = []
        try:
            result = generate_json(prompt, MONITORING_EVALUATION_SCHEMA)
            
            if result.get("change_detected"):
                # Generate Alert Event
                alert_payload = {
                    "log_id": str(uuid.uuid4()),
                    "decision_id": self.decision_id,
                    "event_type": "Environmental Shift",
                    "event_description": result.get("alert_message"),
                    "recalculated_recommendation": result.get("recalculated_recommendation"),
                    "new_confidence": result.get("new_confidence"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                events.append(alert_payload)
                
                # Update confidence and log
                print(f"⚠️ [Monitoring Engine] ALERT: {result.get('alert_message')}")
                print(f"🔄 Recalculated Recommendation: {result.get('recalculated_recommendation')}")
                
        except Exception as e:
            print(f"[Monitoring Engine] Evaluation failed: {e}")
            
        return events

class ContinuousMonitoringPlugin(NeoversePlugin, MonitoringPluginBase):
    """
    Continuous Monitoring Engine.
    Monitors Weather, Market, News, Business KPIs.
    """
    def __init__(self):
        self.active_jobs = []
        
    def initialize(self):
        event_bus.subscribe("DecisionCreated", self.handle_new_decision)
        monitoring_engine.register_plugin(self)

    def handle_new_decision(self, payload: dict):
        decision_id = payload.get("decision_id")
        business_type = payload.get("business_type", "Unknown")
        decision_query = payload.get("decision_query", "Unknown Decision")
        
        if decision_id:
            # Assuming default location/keyword for architecture demo.
            job = ContinuousMonitoringJob(decision_id, business_type, decision_query)
            self.active_jobs.append(job)
            print(f"👁️ [Monitoring Engine] Created monitoring job for Decision: {decision_id}")

    def check_for_events(self, business_state: dict) -> list:
        """
        Called by background loop.
        """
        all_events = []
        for job in self.active_jobs:
            events = job.check_for_changes()
            for event in events:
                # 1. Log every update via EventBus
                event_bus.publish("MonitoringAlert", event)
                
                # 2. Update Confidence (System wide)
                event_bus.publish("ConfidenceUpdated", {
                    "decision_id": event["decision_id"],
                    "new_confidence": event["new_confidence"]
                })
                
                all_events.append(event)
                
        return all_events
