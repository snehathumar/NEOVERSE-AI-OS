import asyncio

class ContinuousMonitoringEngine:
    """
    Event-driven background monitoring engine.
    Listens to streams and triggers events if thresholds are crossed.
    """
    def __init__(self):
        self.subscribers = []
        
    def subscribe(self, callback):
        self.subscribers.append(callback)

    async def ingest_event(self, source: str, data: dict):
        print(f"📡 [Monitoring] Received event from {source}: {data}")
        # Threshold logic would go here. For MVP, we broadcast all events.
        for callback in self.subscribers:
            await callback(source, data)

monitoring_engine = ContinuousMonitoringEngine()
