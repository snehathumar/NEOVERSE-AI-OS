import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from backend.security.models import AuditLog, SecurityContext
from backend.platform.cloud.bigquery_provider import BigQueryProvider
from backend.platform.cloud.logging_provider import cloud_logger

class AuditLogger:
    """
    Produces immutable, append-only security logs to BigQuery.
    """
    def __init__(self):
        self.bq = BigQueryProvider()
        
    def log_event(self, context: SecurityContext, action: str, resource: str, status: str, details: Dict[str, Any]):
        """
        Logs a security or access event.
        """
        log_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            org_id=context.org_id,
            user_id=context.user_id,
            session_id=context.session_id,
            action=action,
            resource=resource,
            status=status,
            details=details
        )
        
        # Log to structured application logs
        cloud_logger.info(f"AUDIT [{status}] {context.user_id}@{context.org_id} performed {action} on {resource}")
        
        # Stream to BigQuery for immutable retention
        self.bq.stream_analytics("audit_logs", log_entry.model_dump())
