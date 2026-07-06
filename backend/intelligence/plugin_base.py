from abc import ABC, abstractmethod
from typing import Dict, Any

class IntelligencePlugin(ABC):
    """
    Base standard for all Phase 11 Future Intelligence Engines.
    Guarantees that every engine can be orchestrated blindly by the OS.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]):
        """Setup initial state, load models or connect to databases."""
        pass
        
    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the core intelligence logic."""
        pass
        
    @abstractmethod
    def validate(self, result: Dict[str, Any]) -> bool:
        """Ensure the generated output meets structural and logical integrity."""
        pass
        
    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Convert the engine's internal state into a clean JSON for the Final Report."""
        pass
