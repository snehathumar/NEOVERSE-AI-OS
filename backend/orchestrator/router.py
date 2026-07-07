import time
import uuid
import traceback
from typing import Dict, Any, Optional
from backend.orchestrator.context_builder import ContextBuilder
from backend.orchestrator.classifier import IntentClassifier
from backend.orchestrator.planner import ExecutionPlanner
from backend.orchestrator.executor import AsyncExecutor, ModuleExecutionError
from backend.orchestrator.composer import ResponseComposer
from backend.orchestrator.registry import module_registry
from backend.memory.manager import MemoryManager
from backend.event_bus import event_bus
from backend.orchestrator import events
from backend.platform.cloud.logging_provider import cloud_logger

class EnterpriseRouter:
    """
    The central AI OS Orchestrator.
    Handles the strict 12-step execution pipeline, partial failures, and explainable routing.
    """
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        
        # Initialize sub-components
        self.memory_manager = MemoryManager(user_id=self.user_id)
        self.context_builder = ContextBuilder(self.memory_manager)
        self.classifier = IntentClassifier()
        self.planner = ExecutionPlanner()
        self.executor = AsyncExecutor(timeout_seconds=45, max_retries=2)
        self.composer = ResponseComposer()
        
        # Ensure registry has loaded modules
        if not module_registry.list_modules():
            module_registry.discover_modules()
            
    async def process_request(self, user_input: str, session_id: str, business_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        routing_trace = {
            "request_id": request_id,
            "user_id": self.user_id,
            "session_id": session_id,
            "stages": []
        }
        
        cloud_logger.info(f"[{request_id}] Incoming request: {user_input[:50]}...")
        event_bus.publish(events.ROUTER_USER_MESSAGE_RECEIVED, {"request_id": request_id, "input": user_input[:50]})
        
        try:
            # 1. & 2. Receive Input & Build Context
            context_start = time.time()
            context = await self.context_builder.build(user_input, session_id)
            if business_state:
                context.business_state = business_state
            
            routing_trace["stages"].append({"stage": "Context Building", "latency": time.time() - context_start})
            event_bus.publish(events.ROUTER_MEMORY_RETRIEVED, {"request_id": request_id, "learnings_count": len(context.relevant_learnings)})

            # 3. & 4. & 5. & 6. & 7. Classify Intent, Domain, Complexity, Urgency, Missing
            class_start = time.time()
            classification = self.classifier.classify(context)
            routing_trace["classification"] = classification
            routing_trace["stages"].append({"stage": "Intent Classification", "latency": time.time() - class_start})
            event_bus.publish(events.ROUTER_INTENT_CLASSIFIED, {"request_id": request_id, "intent": classification.get("intent")})
            
            # 8. & 9. Build Execution Plan
            plan_start = time.time()
            plan = self.planner.create_plan(classification, context)
            routing_trace["execution_plan"] = {
                "parallel_groups": plan.parallel_groups,
                "is_interview_mode": plan.is_interview_mode,
                "priority": plan.priority
            }
            routing_trace["stages"].append({"stage": "Execution Planning", "latency": time.time() - plan_start})
            event_bus.publish(events.ROUTER_PLAN_GENERATED, {"request_id": request_id, "groups": plan.parallel_groups})
            
            # 10. Execute Modules Asynchronously
            exec_start = time.time()
            if plan.is_interview_mode:
                # Bypass heavy execution if we are just asking for missing fields
                raw_results = {}
            else:
                raw_results = await self.executor.execute_plan(plan, context)
            routing_trace["stages"].append({"stage": "Module Execution", "latency": time.time() - exec_start})
            
            # 11. Merge Outputs (Compose)
            comp_start = time.time()
            final_response = self.composer.compose(context, plan, raw_results)
            routing_trace["stages"].append({"stage": "Response Composition", "latency": time.time() - comp_start})
            
            # Finalize Trace
            routing_trace["total_latency"] = time.time() - start_time
            routing_trace["status"] = "success"
            
            # 12. Return Unified Response (with trace attached for Judge Mode)
            final_response["_routing_trace"] = routing_trace
            final_response["_raw_module_outputs"] = raw_results
            event_bus.publish(events.ROUTER_RESPONSE_GENERATED, {"request_id": request_id, "latency": routing_trace["total_latency"]})
            
            # Stream to BigQuery asynchronously
            self._stream_analytics(routing_trace)
            
            return final_response
            
        except ModuleExecutionError as mee:
            # Critical Module Failed - Abort graceful fallback
            routing_trace["total_latency"] = time.time() - start_time
            routing_trace["status"] = "failed"
            routing_trace["error"] = str(mee)
            self._stream_analytics(routing_trace)
            
            return {
                "natural_response": "I'm sorry, a critical internal cognitive module failed. Please try again or check the system health dashboard.",
                "error": str(mee),
                "_routing_trace": routing_trace
            }
        except Exception as e:
            # Unexpected Router Crash
            routing_trace["total_latency"] = time.time() - start_time
            routing_trace["status"] = "crashed"
            routing_trace["error"] = traceback.format_exc()
            self._stream_analytics(routing_trace)
            cloud_logger.error(f"[{request_id}] Router crashed: {traceback.format_exc()}")
            
            return {
                "natural_response": "I experienced a critical system exception while processing your request.",
                "error": str(e),
                "_routing_trace": routing_trace
            }
            
    def _stream_analytics(self, trace: dict):
        try:
            # Send to BigQuery via provider
            from backend.platform.cloud.bigquery_provider import BigQueryProvider
            bq = BigQueryProvider()
            bq.stream_analytics("routing_traces", trace)
        except Exception as e:
            cloud_logger.warning(f"Failed to stream routing trace to BigQuery: {e}")
