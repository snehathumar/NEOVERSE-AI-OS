import importlib
import pkgutil
import inspect
from backend.plugin_base import NeoversePlugin

class PluginManager:
    """
    Automatically discovers and initializes all valid plugins 
    in the backend.plugins package. This means the Core system
    never requires modification when new plugins are added.
    """
    def __init__(self):
        self.plugins = {}

    def load_plugins(self, package_name="backend.plugins"):
        import backend.plugins
        
        # Iterate through all modules in the plugins directory
        for _, module_name, _ in pkgutil.iter_modules(backend.plugins.__path__):
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)
            
            # Find classes that inherit from NeoversePlugin
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, NeoversePlugin) and obj is not NeoversePlugin:
                    # Initialize and store the plugin
                    plugin_instance = obj()
                    plugin_instance.initialize()
                    self.plugins[name] = plugin_instance
                    print(f"[PluginManager] Automatically registered plugin: {name}")

# Global instance
plugin_manager = PluginManager()
