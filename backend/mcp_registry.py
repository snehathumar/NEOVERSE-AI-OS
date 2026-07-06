import importlib
import pkgutil
import inspect
from backend.mcp_tool_base import McpToolBase

class McpRegistry:
    """
    Automatically discovers and loads all valid MCP Tools in the backend.mcp_tools package.
    Ensures zero core changes are required when new tools are added.
    """
    def __init__(self):
        self._tools = {}

    def load_tools(self, package_name="backend.mcp_tools"):
        """Scans the designated package and auto-registers any class inheriting McpToolBase."""
        import backend.mcp_tools
        
        for _, module_name, _ in pkgutil.iter_modules(backend.mcp_tools.__path__):
            full_module_name = f"{package_name}.{module_name}"
            try:
                module = importlib.import_module(full_module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, McpToolBase) and obj is not McpToolBase:
                        tool_instance = obj()
                        self._tools[tool_instance.name] = tool_instance
                        print(f"[MCP Registry] Automatically registered tool: {tool_instance.name}")
            except Exception as e:
                print(f"[MCP Registry] Failed to load module {full_module_name}: {e}")

    def get_all_tool_schemas(self) -> list:
        """
        Returns a list of all tool schemas, which can be injected directly into the LLM prompt.
        """
        schemas = []
        for tool_name, tool in self._tools.items():
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            })
        return schemas

    def execute_tool(self, tool_name: str, inputs: dict) -> dict:
        """
        Executes a registered tool by name.
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found in registry."}
        
        try:
            return tool.execute(inputs)
        except Exception as e:
            return {"error": f"Tool '{tool_name}' execution failed: {str(e)}"}

# Global Registry Instance
mcp_registry = McpRegistry()
