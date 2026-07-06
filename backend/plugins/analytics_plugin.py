from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus

class AnalyticsPlugin(NeoversePlugin):
    def initialize(self):
        # Automatically registers Analytics Service to Event Bus
        from backend.analytics_service import analytics_service
        analytics_service._subscribe_to_events()
