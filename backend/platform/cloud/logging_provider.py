import os
import logging
from typing import Optional

class CloudLogger:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.use_cloud = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
        self._logger = logging.getLogger("neoverse_cloud")
        self._logger.setLevel(logging.INFO)
        
        # Add a local console handler if none exist
        if not self._logger.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self._logger.addHandler(ch)

        self.cloud_enabled = False
        if self.use_cloud and self.project_id:
            try:
                from google.cloud import logging as cloud_logging
                client = cloud_logging.Client(project=self.project_id)
                client.setup_logging()
                self.cloud_enabled = True
                self.info("Cloud Logging initialized successfully.")
            except ImportError:
                self.warning("google-cloud-logging not installed. Falling back to local logging.")
            except Exception as e:
                self.warning(f"Failed to initialize Cloud Logging: {e}. Falling back to local logging.")

    def health_check(self) -> bool:
        if not self.cloud_enabled: return False
        try:
            # simple import check or basic setup check
            import google.cloud.logging
            return True
        except Exception:
            return False

    def _log_struct(self, msg: str, severity: str, extra: dict = None):
        """Helper to send structured JSON logs to GCP, or fallback to local"""
        payload = {
            "message": msg, 
            "severity": severity,
            "environment": os.getenv("NEOVERSE_ENV", "production"),
            "session_id": os.getenv("NEOVERSE_SESSION_ID", "system"),
            "user_id": os.getenv("NEOVERSE_USER_ID", "system")
        }
        if extra:
            payload.update(extra)

        if self.cloud_enabled:
            try:
                import google.cloud.logging as cloud_logging
                client = cloud_logging.Client(project=self.project_id)
                logger = client.logger("neoverse_structured_logs")
                logger.log_struct(payload, severity=severity)
                return
            except Exception as e:
                self._logger.warning(f"Failed structured log to GCP: {e}")
        
        # Local fallback
        import json
        if severity in ["ERROR", "CRITICAL", "EXCEPTION"]:
            self._logger.error(json.dumps(payload))
        elif severity == "WARNING":
            self._logger.warning(json.dumps(payload))
        else:
            self._logger.info(json.dumps(payload))

    def info(self, msg: str, **kwargs):
        self._log_struct(msg, "INFO", kwargs)

    def warning(self, msg: str, **kwargs):
        self._log_struct(msg, "WARNING", kwargs)

    def error(self, msg: str, **kwargs):
        self._log_struct(msg, "ERROR", kwargs)
        
    def exception(self, msg: str, **kwargs):
        self._log_struct(msg, "EXCEPTION", kwargs)

    def get_agent_logger(self, agent_name: str):
        """Returns a scoped logger for a specific agent."""
        class AgentLogger:
            def info(self_, msg, **kwargs): self.info(msg, agent=agent_name, **kwargs)
            def warning(self_, msg, **kwargs): self.warning(msg, agent=agent_name, **kwargs)
            def error(self_, msg, **kwargs): self.error(msg, agent=agent_name, **kwargs)
            def exception(self_, msg, **kwargs): self.exception(msg, agent=agent_name, **kwargs)
        return AgentLogger()

    def get_system_logger(self):
        """Returns a scoped logger for system events."""
        class SystemLogger:
            def info(self_, msg, **kwargs): self.info(msg, component="system", **kwargs)
            def warning(self_, msg, **kwargs): self.warning(msg, component="system", **kwargs)
            def error(self_, msg, **kwargs): self.error(msg, component="system", **kwargs)
            def exception(self_, msg, **kwargs): self.exception(msg, component="system", **kwargs)
        return SystemLogger()

    def get_performance_logger(self):
        """Returns a scoped logger for performance events."""
        class PerfLogger:
            def info(self_, msg, **kwargs): self.info(msg, component="performance", **kwargs)
            def warning(self_, msg, **kwargs): self.warning(msg, component="performance", **kwargs)
            def error(self_, msg, **kwargs): self.error(msg, component="performance", **kwargs)
            def exception(self_, msg, **kwargs): self.exception(msg, component="performance", **kwargs)
        return PerfLogger()

# Singleton instance for easy import
cloud_logger = CloudLogger()
