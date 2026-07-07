import asyncio
import time
from typing import Dict, Any, List
from backend.orchestrator.planner import ExecutionPlan
from backend.orchestrator.registry import module_registry
from backend.orchestrator.context_builder import UnifiedContext
from backend.platform.cloud.logging_provider import cloud_logger
from backend.event_bus import event_bus
from backend.orchestrator import events

class ModuleExecutionError(Exception):
    pass

class AsyncExecutor:
    """
    Executes the ExecutionPlan.
    Supports timeouts, retries, and partial failure strategies.
    Streams progress via EventBus.
    """
    def __init__(self, timeout_seconds: int = 30, max_retries: int = 2):
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        
    async def execute_plan(self, plan: ExecutionPlan, context: UnifiedContext) -> Dict[str, Any]:
        results = {}
        
        # Publish start event for streaming
        event_bus.publish(events.ROUTER_MODULE_STARTED, {"plan_priority": plan.priority})
        
        # We iterate over parallel groups. Groups run sequentially, modules within a group run parallel.
        for group in plan.parallel_groups:
            cloud_logger.info(f"Executing parallel group: {group}")
            
            tasks = []
            for module_name in group:
                tasks.append(self._execute_module_with_retry(module_name, context, results))
                
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for mod_name, res in zip(group, group_results):
                if isinstance(res, Exception):
                    cloud_logger.error(f"Module {mod_name} failed: {res}")
                    module = module_registry.get_module(mod_name)
                    if module.is_critical:
                        cloud_logger.critical(f"Critical module {mod_name} failed. Halting Execution.")
                        event_bus.publish(events.ROUTER_MODULE_FAILED, {"module": mod_name, "critical": True})
                        raise ModuleExecutionError(f"Critical module {mod_name} failed: {res}")
                    else:
                        cloud_logger.warning(f"Non-critical module {mod_name} failed. Proceeding.")
                        event_bus.publish(events.ROUTER_MODULE_FAILED, {"module": mod_name, "critical": False})
                        results[mod_name] = {"error": str(res), "status": "failed"}
                else:
                    results[mod_name] = res
                    event_bus.publish(events.ROUTER_MODULE_COMPLETED, {"module": mod_name})
                    
        return results

    async def _execute_module_with_retry(self, module_name: str, context: UnifiedContext, current_results: Dict[str, Any]):
        module = module_registry.get_module(module_name)
        
        # Convert context to dict for module consumption, appending upstream results
        exec_context = {
            "user_input": context.user_input,
            "session_id": context.session_id,
            "business_state": context.business_state,
            "upstream_results": current_results
        }
        
        if not await module.validate(exec_context):
            raise ValueError(f"Validation failed for module {module_name}")
            
        for attempt in range(self.max_retries):
            try:
                # Enforce timeout using asyncio.wait_for
                start_time = time.time()
                result = await asyncio.wait_for(module.execute(exec_context), timeout=self.timeout_seconds)
                latency = time.time() - start_time
                cloud_logger.info(f"Module {module_name} succeeded in {latency:.2f}s")
                return result
            except asyncio.TimeoutError:
                cloud_logger.warning(f"Module {module_name} timed out (Attempt {attempt + 1}/{self.max_retries})")
            except Exception as e:
                cloud_logger.warning(f"Module {module_name} error: {e} (Attempt {attempt + 1}/{self.max_retries})")
                
            # If we reach here, we failed this attempt. Backoff slightly before retry.
            await asyncio.sleep(1)
            
        if 'e' in locals():
            raise Exception(f"Module {module_name} exhausted all {self.max_retries} retries. Last error: {e}")
        else:
            raise Exception(f"Module {module_name} exhausted all {self.max_retries} retries.")
