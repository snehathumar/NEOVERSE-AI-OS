from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PluginPermission(BaseModel):
    scope: str # e.g. read_memory, execute_tool, access_report
    description: str

class PluginManifest(BaseModel):
    plugin_id: str
    name: str
    version: str
    developer_id: str
    description: str
    permissions: List[PluginPermission]
    source_url: str # GitHub URL or Cloud Storage URI
    entrypoint: str # e.g. "plugin.main:NeoversePlugin"
    revenue_share_percentage: float = 0.70 # Default 70% to dev
    price_per_execution: float = 0.0 # Pay per use
    is_webhook: bool = False # If true, it's a REST plugin, not Python
    webhook_url: Optional[str] = None
    checksum: str # SHA-256 for verification

class MarketplaceEvent(BaseModel):
    event_id: str
    org_id: str
    plugin_id: str
    event_type: str # plugin_installed, plugin_executed, plugin_billed, plugin_failed
    timestamp: str
    details: Dict[str, Any]

class PluginInstallation(BaseModel):
    org_id: str
    plugin_id: str
    installed_version: str
    status: str # active, suspended, blacklisted
    granted_scopes: List[str]
