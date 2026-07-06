import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ExecutionModule(ABC):
    """
    Base plugin architecture for all NEOVERSE backend capabilities.
    Every engine must implement this interface to be orchestrated.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the module (e.g., 'DecisionEngine')"""
        pass
        
    @property
    @abstractmethod
    def is_critical(self) -> bool:
        """If true, failure of this module fails the entire workflow."""
        pass
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Setup connections, load cache. Return True if successful."""
        pass
        
    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Check if the context has all required inputs for this module."""
        pass
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic. Returns result dictionary."""
        pass
        
    @abstractmethod
    async def cancel(self) -> bool:
        """Gracefully halt execution if orchestrator cancels."""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Free resources after execution."""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Quick health probe."""
        pass
