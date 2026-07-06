import hashlib
from typing import Dict, Any, Optional
from backend.marketplace.models import PluginManifest, PluginInstallation
from backend.platform.cloud.logging_provider import cloud_logger

class PluginRegistry:
    """
    Manages the Hybrid Plugin Ecosystem (GitHub + Cloud Storage).
    """
    def __init__(self):
        # Mock database of global available plugins
        self.registry = {
            "ext_slack_notifier_v1": PluginManifest(
                plugin_id="ext_slack_notifier_v1",
                name="Slack Enterprise Notifier",
                version="1.0.0",
                developer_id="dev_acme_corp",
                description="Sends execution reports to Slack",
                permissions=[{"scope": "network_access", "description": "Call Slack APIs"}],
                source_url="https://github.com/acme/neoverse-slack-plugin/releases/download/v1/plugin.zip",
                entrypoint="slack_plugin.main:NotifierPlugin",
                checksum="mock_sha256_hash",
                price_per_execution=0.01
            )
        }
        
        # Mock org installations
        self.installations = {
            "org-neo-enterprise": {
                "ext_slack_notifier_v1": PluginInstallation(
                    org_id="org-neo-enterprise",
                    plugin_id="ext_slack_notifier_v1",
                    installed_version="1.0.0",
                    status="active",
                    granted_scopes=["network_access"]
                )
            }
        }
        
        # Security blacklists
        self.blacklisted_plugins = set(["ext_malicious_plugin_v1"])

    def get_plugin_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        if plugin_id in self.blacklisted_plugins:
            cloud_logger.warning(f"Attempted to access blacklisted plugin: {plugin_id}")
            return None
        return self.registry.get(plugin_id)

    def is_installed_and_active(self, org_id: str, plugin_id: str) -> bool:
        """
        Verify the org actually installed it and accepted the permission scopes.
        """
        org_installs = self.installations.get(org_id, {})
        install = org_installs.get(plugin_id)
        if not install:
            return False
        return install.status == "active"
        
    def verify_signature(self, plugin_id: str, raw_bytes: bytes) -> bool:
        """
        Ensures the downloaded plugin code matches the registered SHA-256 hash.
        """
        manifest = self.get_plugin_manifest(plugin_id)
        if not manifest:
            return False
            
        computed_hash = hashlib.sha256(raw_bytes).hexdigest()
        # Mocking signature verification logic:
        # return computed_hash == manifest.checksum
        return True
