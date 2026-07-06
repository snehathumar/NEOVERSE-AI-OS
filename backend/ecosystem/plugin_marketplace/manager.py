from typing import List, Dict, Any

class PluginMarketplaceManager:
    """
    Manages drop-in industry plugins (Finance, Healthcare, Agriculture, etc).
    Registers them without requiring core OS code modifications.
    """
    def __init__(self):
        self.installed_plugins: List[Dict[str, Any]] = []
        
    def install_plugin(self, manifest: Dict[str, Any]):
        plugin_name = manifest.get("name")
        self.installed_plugins.append(manifest)
        print(f"🛍️ [Marketplace] Installed Industry Plugin: {plugin_name}")
        
    def get_installed_plugins(self) -> List[Dict[str, Any]]:
        return self.installed_plugins

marketplace_manager = PluginMarketplaceManager()
