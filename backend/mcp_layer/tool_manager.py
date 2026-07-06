import json
from backend.mcp_layer.tool_registry import tool_registry
from backend.mcp_layer.cache_manager import cache_manager
from backend.mcp_layer.health_monitor import health_monitor
import time

class ToolManager:
    """
    The only component allowed to communicate with external APIs via registered tools.
    Handles caching, execution, and fallback strategies.
    """
    
    def execute_tool(self, tool_name: str, params: dict) -> dict:
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found."}
            
        # Check cache
        cache_key = f"{tool_name}_{json.dumps(params, sort_keys=True)}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            print(f"⚡ [ToolManager] Cache Hit for {tool_name}")
            return cached_result
            
        # Check health
        if not health_monitor.is_healthy(f"tool_{tool_name}"):
            return {"error": "API in cooldown", "fallback_data": "Returning historical averages..."}

        print(f"🌍 [ToolManager] Executing API Call: {tool_name}")
        start_time = time.time()
        
        try:
            result = tool.execute(**params)
            latency = int((time.time() - start_time) * 1000)
            
            # Record success and cache
            health_monitor.record_success(f"tool_{tool_name}", latency)
            cache_manager.set(cache_key, result, ttl_seconds=600)
            
            return result
        except Exception as e:
            print(f"❌ [ToolManager] Tool {tool_name} failed: {e}")
            health_monitor.record_failure(f"tool_{tool_name}", cooldown_seconds=300)
            # Never crash. Return graceful fallback.
            return {"error": str(e), "fallback_data": "Simulated fallback data activated."}

tool_manager = ToolManager()
