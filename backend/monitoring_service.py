import threading
import time
import uuid
from datetime import datetime, timezone
from backend.analytics_service import analytics_service

class MonitoringPluginBase:
    """
    Base class for future monitoring plugins.
    Plugins should inherit this and implement the check_for_events() method.
    """
    def check_for_events(self, business_state: dict):
        raise NotImplementedError("Plugins must implement check_for_events()")


class MonitoringEngine:
    """
    A generic background monitoring framework.
    Continuously monitors the business state by executing registered plugins.
    """
    def __init__(self, check_interval_seconds: int = 3600):
        self.check_interval_seconds = check_interval_seconds
        self.plugins = []
        self._is_running = False
        self._monitor_thread = None

    def register_plugin(self, plugin: MonitoringPluginBase):
        """Allows future modules to inject external API monitoring hooks."""
        self.plugins.append(plugin)

    def start_monitoring(self, user_id: str, business_state: dict):
        """Starts the background scheduler loop."""
        if self._is_running:
            return
            
        self._is_running = True
        self._monitor_thread = threading.Thread(
            target=self._run_scheduler, 
            args=(user_id, business_state,),
            daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self):
        """Stops the background loop."""
        self._is_running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)

    def _run_scheduler(self, user_id: str, business_state: dict):
        """
        Background Scheduler Loop.
        Workflow: Event detection -> Decision update -> Alert generation -> Monitoring log
        """
        while self._is_running:
            for plugin in self.plugins:
                try:
                    events = plugin.check_for_events(business_state)
                    if events:
                        self._process_events(user_id, events)
                except Exception as e:
                    print(f"Monitoring Plugin Error: {e}")
            
            # Wait for the next cycle
            time.sleep(self.check_interval_seconds)

    def _process_events(self, user_id: str, events: list):
        """Processes detected events, generates alerts, and logs to BigQuery."""
        monitoring_logs = []
        
        for event in events:
            # 1. Decision Update (Mock logic placeholder)
            # e.g., triggering the recommendation_update_engine based on the event
            
            # 2. Alert Generation
            alert_id = str(uuid.uuid4())
            print(f"⚠️ [MONITORING ALERT] {event.get('title')}: {event.get('description')}")
            
            # 3. Monitoring Log Preparation
            log_row = {
                "log_id": alert_id,
                "user_id": user_id,
                "event_type": event.get("type", "unknown"),
                "event_description": event.get("description", ""),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            monitoring_logs.append(log_row)

        # Publish directly to Event Bus
        if monitoring_logs:
            try:
                from backend.event_bus import event_bus
                for log in monitoring_logs:
                    event_bus.publish("MonitoringAlert", log)
            except Exception as e:
                print(f"Failed to publish MonitoringAlert event: {e}")

# Singleton instance
monitoring_engine = MonitoringEngine()
