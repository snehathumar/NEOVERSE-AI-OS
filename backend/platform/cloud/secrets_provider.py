import os
from typing import Optional
from backend.platform.cloud.logging_provider import cloud_logger

class SecretsProvider:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.use_cloud = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
        self.client = None

        if self.use_cloud and self.project_id:
            try:
                from google.cloud import secretmanager
                self.client = secretmanager.SecretManagerServiceClient()
                cloud_logger.info("Secret Manager initialized successfully.")
            except ImportError:
                cloud_logger.warning("google-cloud-secret-manager not installed. Secrets will fallback to .env.")
            except Exception as e:
                cloud_logger.warning(f"Failed to initialize Secret Manager: {e}. Falling back to .env.")

    def health_check(self) -> bool:
        """Pings Secret Manager to ensure connection is active."""
        if not self.client: return False
        try:
            # simple metadata query (list secrets, limit 1)
            parent = f"projects/{self.project_id}"
            list(self.client.list_secrets(request={"parent": parent, "page_size": 1}))
            return True
        except Exception:
            return False

    def get_secret(self, secret_id: str, version_id: str = "latest") -> Optional[str]:
        """
        Attempts to fetch a secret from GCP Secret Manager.
        If it fails or is unavailable, falls back to local environment variables (.env).
        """
        if self.client and self.project_id:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
                response = self.client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
            except Exception as e:
                cloud_logger.warning(f"Failed to fetch secret '{secret_id}' from GCP: {e}. Falling back to env.")

        # Graceful fallback to .env
        env_val = os.getenv(secret_id)
        if env_val:
            return env_val
            
        cloud_logger.error(f"Secret '{secret_id}' not found in Secret Manager or .env")
        return None

secrets_provider = SecretsProvider()
