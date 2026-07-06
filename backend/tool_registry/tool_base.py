from abc import ABC, abstractmethod
from typing import Dict, Type

class BaseTool(ABC):
    """
    Abstract Base Class for all MCP Tools.
    """
    @property
    @abstractmethod
    def name(self) -> str: pass
    
    @property
    @abstractmethod
    def description(self) -> str: pass

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """Executes the tool and returns raw JSON data."""
        pass


class MCPToolRegistry:
    """
    Dynamically registers and holds all available tools.
    Future tools must auto-register themselves here.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_class: Type[BaseTool]):
        tool_instance = tool_class()
        self._tools[tool_instance.name] = tool_instance
        print(f"🔧 [ToolRegistry] Registered Plugin: {tool_instance.name}")

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def get_all_tools(self) -> Dict[str, BaseTool]:
        return self._tools

tool_registry = MCPToolRegistry()
