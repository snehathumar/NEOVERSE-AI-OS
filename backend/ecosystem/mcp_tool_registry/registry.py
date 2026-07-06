from abc import ABC, abstractmethod
from typing import Dict, Any
import html

class MCPTool(ABC):
    """Base class for all Enterprise MCP Tools."""
    @abstractmethod
    def initialize(self): pass
    @abstractmethod
    def health_check(self) -> bool: pass
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any: pass
    @abstractmethod
    def normalize_output(self, raw_output: Any) -> Dict[str, Any]: pass
    @abstractmethod
    def fallback(self) -> Dict[str, Any]: pass
    @abstractmethod
    def metadata(self) -> Dict[str, Any]: pass

class EnterpriseToolRegistry:
    """
    Centralized Tool Registry with strict Input/Output sanitization 
    and Graceful Degradation.
    """
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        
    def register_tool(self, name: str, tool: MCPTool):
        self.tools[name] = tool
        print(f"🧰 [ToolRegistry] Registered Tool: {name}")

    def _sanitize_input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prevents injection attacks by sanitizing string inputs."""
        sanitized = {}
        for k, v in params.items():
            if isinstance(v, str):
                sanitized[k] = html.escape(v)
            else:
                sanitized[k] = v
        return sanitized

    def execute_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            return {"error": f"Tool {name} not found in registry."}
            
        tool = self.tools[name]
        sanitized_params = self._sanitize_input(params)
        
        if not tool.health_check():
            print(f"⚠️ [ToolRegistry] {name} failed health check. Using fallback.")
            return tool.fallback()
            
        try:
            raw = tool.execute(sanitized_params)
            return tool.normalize_output(raw)
        except Exception as e:
            print(f"🚨 [ToolRegistry] {name} execution failed: {e}. Using fallback.")
            return tool.fallback()

tool_registry = EnterpriseToolRegistry()
