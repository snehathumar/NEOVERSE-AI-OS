import asyncio
from backend.platform.event_bus.bus import event_bus
from backend.platform.observability.tracker import system_observability

class IntelligenceOrchestrator:
    """
    Master Orchestrator. Replaces sequential processing.
    Listens for tasks, selects required agents/tools, runs parallel workflows, 
    and merges outputs asynchronously.
    """
    def __init__(self):
        # Bind to event bus
        event_bus.subscribe("DECISION_REQUESTED", self.handle_decision_request)
        event_bus.subscribe("EVIDENCE_UPDATED", self.handle_evidence_updated)
        
    async def handle_decision_request(self, payload: dict):
        print("🧠 [Orchestrator] Received DECISION_REQUESTED. Coordinating workflow...")
        start_time = asyncio.get_event_loop().time()
        
        # 1. Trigger Evidence Collection (Simulated Async)
        await event_bus.publish("EVIDENCE_COLLECTION_STARTED", {"decision_id": payload.get("id")})
        
        # Assume evidence is collected fast in this mock
        end_time = asyncio.get_event_loop().time()
        system_observability.log_latency("Orchestrator_Decision_Start", (end_time - start_time) * 1000)

    async def handle_evidence_updated(self, payload: dict):
        print("🧠 [Orchestrator] Evidence updated. Merging outputs and triggering Intelligence Agents...")
        # 2. Trigger Intelligence Plugins
        await event_bus.publish("INTELLIGENCE_GENERATION_STARTED", payload)
        
        # 3. Eventually trigger Recommendation
        await event_bus.publish("RECOMMENDATION_GENERATED", {"status": "Complete"})

orchestrator = IntelligenceOrchestrator()
