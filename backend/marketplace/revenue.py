from backend.marketplace.models import PluginManifest
from backend.billing.metering import UsageMeteringEngine

class RevenueSplitEngine:
    """
    Calculates developer vs platform commission splits based on the marketplace billing configuration.
    """
    def __init__(self):
        self.metering = UsageMeteringEngine()
        
    def log_plugin_usage(self, org_id: str, user_id: str, manifest: PluginManifest, executions: int = 1):
        """
        Calculates the revenue split based on price_per_execution and revenue_share_percentage.
        Logs to UsageMeteringEngine for month-end payouts.
        """
        total_revenue = manifest.price_per_execution * executions
        developer_cut = total_revenue * manifest.revenue_share_percentage
        platform_cut = total_revenue - developer_cut
        
        # We overload the metering engine to log revenue events as well as usage events
        self.metering.record_marketplace_usage(
            org_id=org_id,
            user_id=user_id,
            plugin_id=manifest.plugin_id,
            developer_id=manifest.developer_id,
            total_revenue=total_revenue,
            developer_cut=developer_cut,
            platform_cut=platform_cut
        )
