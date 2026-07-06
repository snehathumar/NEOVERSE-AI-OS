import asyncio
from backend.living_layer.change_detector import change_detector

class ContinuousMonitoringEngine:
    """
    Background worker that simulates observing live signals.
    """
    def simulate_incoming_signal(self, raw_signal: dict, business_state: dict):
        """
        Simulates receiving a real-time webhook or scheduled poll of Market Trends, News, etc.
        Passes the signal to the Change Detector.
        """
        print(f"📡 [Monitoring Engine] Received Signal: {raw_signal.get('headline', 'Unknown')}")
        detection = change_detector.detect_change(raw_signal, business_state)
        
        if detection.get("is_meaningful"):
            print(f"🚨 [Monitoring Engine] Meaningful Change Detected: {detection.get('impact_category')}")
        else:
            print("💤 [Monitoring Engine] Signal ignored (Noise).")
            
        return detection

monitoring_engine = ContinuousMonitoringEngine()
