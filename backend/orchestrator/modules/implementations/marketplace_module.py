from backend.orchestrator.modules.base import ExecutionModule
from backend.marketplace.registry import PluginRegistry
from backend.marketplace.sandbox import SandboxExecutionEngine
from backend.marketplace.revenue import RevenueSplitEngine
from backend.security.models import SecurityContext
from backend.platform.cloud.logging_provider import cloud_logger

class MarketplaceModule(ExecutionModule):
    """
    Executes third-party marketplace plugins via the secure Sandbox Engine.
    """
    def __init__(self):
        self.registry = PluginRegistry()
        self.sandbox = SandboxExecutionEngine()
        self.revenue = RevenueSplitEngine()
        
    @property
    def name(self) -> str:
        return "MarketplaceModule"

    @property
    def is_critical(self) -> bool:
        return False # If a third-party plugin fails, the core pipeline should not crash

    async def initialize(self) -> bool:
        return True

    async def validate(self, context: dict) -> bool:
        # We only execute if the user requested a specific third-party plugin execution
        req = context.get("user_request", {})
        return "target_plugin_id" in req

    async def execute(self, context: dict) -> dict:
        req = context.get("user_request", {})
        plugin_id = req.get("target_plugin_id")
        sec_context_dict = context.get("security_context", {})
        
        # Hydrate security context
        sec_context = SecurityContext(**sec_context_dict) if sec_context_dict else None
        
        if not sec_context:
            raise PermissionError("Missing Security Context in MarketplaceModule.")
            
        # 1. Check if org installed it and plugin is active
        if not self.registry.is_installed_and_active(sec_context.org_id, plugin_id):
            raise PermissionError(f"Plugin {plugin_id} is not installed or active for this organization.")
            
        # 2. Get manifest and verify
        manifest = self.registry.get_plugin_manifest(plugin_id)
        if not manifest:
            raise ValueError(f"Plugin {plugin_id} not found in global registry.")
            
        # 3. RBAC validation (mocked for now, assumes user role permits plugin execution)
        
        try:
            # 4. Execute inside Sandbox
            sandbox_result = await self.sandbox.execute_plugin(manifest, input_data=req.get("plugin_payload", {}))
            
            # 5. Track Usage & Split Revenue
            self.revenue.log_plugin_usage(
                org_id=sec_context.org_id,
                user_id=sec_context.user_id,
                manifest=manifest,
                executions=1
            )
            
            return {
                "status": "success",
                "plugin_id": plugin_id,
                "result": sandbox_result
            }
            
        except Exception as e:
            cloud_logger.error(f"MarketplaceModule execution failed for {plugin_id}: {e}")
            raise

    async def cancel(self) -> bool:
        return True

    async def cleanup(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True
