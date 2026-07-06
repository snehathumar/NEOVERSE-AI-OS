import json
import time
from backend.tool_registry.tool_base import tool_registry
from backend.cache.cache_manager import cache_manager
from backend.monitoring.api_monitor import api_monitor
from backend.normalizer.normalizer import normalizer

class ToolManager:
    """
    The only component allowed to communicate with external APIs.
    Gemini requests capabilities; ToolManager orchestrates Execution -> Cache -> Normalization.
    """
    def execute_capability(self, capability: str, params: dict, category: str = "General") -> dict:
        tool = tool_registry.get_tool(capability)
        if not tool:
            return normalizer.normalize("Unknown", {"error": f"Capability '{capability}' not found.", "fallback_data": {}})
            
        # Check Cache
        cache_key = f"{capability}_{json.dumps(params, sort_keys=True)}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            print(f"⚡ [ToolManager] Cache Hit for {capability}")
            # Still wrap in evidence, just maybe mark freshness differently
            evidence = normalizer.normalize(capability, cached_result, category)
            evidence["freshness"] = "Cached"
            return evidence
            
        print(f"🌍 [ToolManager] Executing External API Call for: {capability}")
        start_time = time.time()
        
        try:
            # Execute
            raw_result = tool.execute(**params)
            latency = int((time.time() - start_time) * 1000)
            
            # Monitoring
            api_monitor.record_success(capability, latency)
            
            # Caching
            cache_manager.set(cache_key, raw_result, ttl_seconds=600)
            
            # Normalization
            return normalizer.normalize(capability, raw_result, category)
            
        except Exception as e:
            print(f"❌ [ToolManager] API {capability} failed: {e}")
            api_monitor.record_failure(capability, str(e))
            
            # Fallback System: Graceful Degradation
            fallback = {"error": str(e), "fallback_data": {"note": "Simulated fallback data to prevent crash."}}
            return normalizer.normalize(capability, fallback, category)

tool_manager = ToolManager()
