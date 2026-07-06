from backend.plugin_base import NeoversePlugin
from backend.event_bus import event_bus

class LearningPlugin(NeoversePlugin):
    def initialize(self):
        event_bus.subscribe("PredictionUpdated", self.handle_prediction)
        
    def handle_prediction(self, payload):
        pass
