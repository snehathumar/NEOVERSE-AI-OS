import abc
from typing import Dict, Any

class BaseActionPlugin(abc.ABC):
    """
    Interface for all Execution Plugins.
    Ensures safe execution and mandatory rollback implementation.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    async def execute(self, action_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the real-world action."""
        pass

    @abc.abstractmethod
    async def rollback(self, action_name: str, execution_result: Dict[str, Any], rollback_steps: Dict[str, Any]) -> bool:
        """Undo the real-world action if a downstream dependency fails."""
        pass

    @abc.abstractmethod
    async def health_check(self) -> bool:
        """Verify the plugin is capable of executing (e.g. API keys are valid)."""
        pass
