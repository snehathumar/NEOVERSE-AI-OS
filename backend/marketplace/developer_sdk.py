from typing import Dict, Any, Optional

class NeoversePluginBase:
    """
    The Base SDK Class that all third-party Python developers must inherit from.
    This guarantees the Sandbox Engine knows how to invoke the code.
    """
    
    def __init__(self, plugin_context: Dict[str, Any]):
        self.context = plugin_context
        # context contains granted permissions, org_id, etc.
        
    async def pre_execute(self) -> bool:
        """
        Hook called before the main execution.
        Return False to abort execution.
        """
        return True
        
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main business logic of the plugin.
        MUST be implemented by the developer.
        """
        raise NotImplementedError("Plugins must implement the execute method.")
        
    async def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook called after execution to mutate results or perform cleanup.
        """
        return result
        
    async def on_error(self, error: Exception) -> None:
        """
        Hook called if execution throws an unhandled exception.
        """
        pass
