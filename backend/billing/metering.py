import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from backend.billing.models import UsageRecord
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class UsageMeteringEngine:
    """
    Non-blocking, eventual consistency usage tracking.
    Streams usage to BigQuery async to prevent API latency.
    """
    def __init__(self):
        self.bq = BigQueryProvider()
        
    def record_usage(self, org_id: str, user_id: str, resource_type: str, quantity: int, module_name: str):
        """
        Fire-and-forget usage tracking.
        In production, this pushes to a Redis queue or EventBus first, 
        and a background worker flushes to BigQuery.
        Here we simulate that async behavior.
        """
        asyncio.create_task(self._async_push_to_bq(
            org_id, user_id, resource_type, quantity, module_name
        ))
        
    async def _async_push_to_bq(self, org_id: str, user_id: str, resource_type: str, quantity: int, module_name: str):
        try:
            record = UsageRecord(
                record_id=str(uuid.uuid4()),
                org_id=org_id,
                user_id=user_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                resource_type=resource_type,
                quantity=quantity,
                module_name=module_name
            )
            
            # Stream to BigQuery `usage_metrics` dataset
            self.bq.stream_analytics("usage_metrics", record.model_dump())
            cloud_logger.debug(f"Metered {quantity} {resource_type} for org {org_id} via {module_name}")
            
        except Exception as e:
            # If BQ fails, we must fall back to logging so usage isn't lost
            cloud_logger.error(f"Usage metering BQ failure: {e}")
            cloud_logger.info(f"FALLBACK_METERING: org_id={org_id}, resource={resource_type}, qty={quantity}")
            
    def record_marketplace_usage(self, org_id: str, user_id: str, plugin_id: str, developer_id: str, total_revenue: float, developer_cut: float, platform_cut: float):
        """
        Records financial usage data for third-party marketplace plugins.
        """
        asyncio.create_task(self._async_push_marketplace_to_bq(
            org_id, user_id, plugin_id, developer_id, total_revenue, developer_cut, platform_cut
        ))
        
    async def _async_push_marketplace_to_bq(self, org_id: str, user_id: str, plugin_id: str, developer_id: str, total_revenue: float, developer_cut: float, platform_cut: float):
        try:
            record = {
                "record_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "org_id": org_id,
                "user_id": user_id,
                "plugin_id": plugin_id,
                "developer_id": developer_id,
                "total_revenue": total_revenue,
                "developer_cut": developer_cut,
                "platform_cut": platform_cut
            }
            # Stream to BigQuery `marketplace_usage_events` dataset
            self.bq.stream_analytics("marketplace_usage_events", record)
            cloud_logger.debug(f"Metered Marketplace Usage for plugin {plugin_id}")
        except Exception as e:
            cloud_logger.error(f"Marketplace usage BQ failure: {e}")
