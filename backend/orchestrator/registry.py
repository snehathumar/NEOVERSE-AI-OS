import importlib
import inspect
import pkgutil
from typing import Dict, Type
from backend.orchestrator.modules.base import ExecutionModule
from backend.platform.cloud.logging_provider import cloud_logger

class ModuleRegistry:
    """
    Dynamic Module Registry for the Enterprise AI Router.
    Automatically discovers and registers all ExecutionModules during startup.
    """
    def __init__(self):
        self._modules: Dict[str, ExecutionModule] = {}
        
    def discover_modules(self, package_name: str = "backend.orchestrator.modules.implementations"):
        """Scans the implementations directory and auto-registers valid ExecutionModules."""
        cloud_logger.info(f"Discovering ExecutionModules in {package_name}...")
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            cloud_logger.warning(f"Module package {package_name} not found. No modules loaded.")
            return

        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package_name}.{module_name}"
            try:
                mod = importlib.import_module(full_module_name)
                for name, obj in inspect.getmembers(mod):
                    if inspect.isclass(obj) and issubclass(obj, ExecutionModule) and obj is not ExecutionModule:
                        instance = obj()
                        self.register(instance)
            except Exception as e:
                cloud_logger.error(f"Failed to load module {full_module_name}: {e}")

    def register(self, module: ExecutionModule):
        """Registers a specific module instance."""
        if module.name in self._modules:
            cloud_logger.warning(f"Module {module.name} is already registered. Overwriting.")
        self._modules[module.name] = module
        cloud_logger.info(f"Successfully registered ExecutionModule: {module.name} (Critical: {module.is_critical})")
        
    def get_module(self, name: str) -> ExecutionModule:
        """Retrieves a registered module by name."""
        if name not in self._modules:
            raise KeyError(f"ExecutionModule '{name}' not found in registry.")
        return self._modules[name]
        
    def list_modules(self) -> Dict[str, bool]:
        """Returns map of module names to their critical status."""
        return {name: mod.is_critical for name, mod in self._modules.items()}

# Singleton Registry
module_registry = ModuleRegistry()
