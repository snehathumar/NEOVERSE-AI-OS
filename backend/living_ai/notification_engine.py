import time
from typing import List

class NotificationEngine:
    """
    Intelligent alert dispatcher.
    """
    def __init__(self):
        self.active_alerts = []

    def dispatch_alert(self, priority: str, reason: str, evidence: dict, recommended_action: str):
        alert = {
            "id": f"alert_{int(time.time()*1000)}",
            "priority": priority,
            "reason": reason,
            "evidence": evidence,
            "recommended_action": recommended_action,
            "timestamp": time.time()
        }
        self.active_alerts.append(alert)
        print(f"🔔 [Notification] {priority.upper()} Alert: {reason}")
        return alert
        
    def get_active_alerts(self) -> List[dict]:
        return self.active_alerts

notification_engine = NotificationEngine()
