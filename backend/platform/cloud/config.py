import os
from typing import Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class CloudConfig:
    """
    Centralized configuration manager for NEOVERSE AI OS cloud integrations.
    Reads all config strictly from environment variables (e.g., .env).
    No hardcoded project IDs or dataset names.
    """
    @property
    def project_id(self) -> Optional[str]:
        return os.getenv("GOOGLE_CLOUD_PROJECT_ID")

    @property
    def is_cloud_enabled(self) -> bool:
        return os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"

    @property
    def gcs_bucket_name(self) -> Optional[str]:
        return os.getenv("NEOVERSE_GCS_BUCKET")

    @property
    def bq_dataset(self) -> str:
        return os.getenv("NEOVERSE_BQ_DATASET", "neoverse_ai")

    @property
    def gemini_api_key(self) -> Optional[str]:
        from backend.platform.cloud.secrets_provider import secrets_provider
        val = secrets_provider.get_secret("GEMINI_API_KEY")
        if not val:
            val = os.getenv("GEMINI_API_KEY")
        return val

    @property
    def signed_url_expiration_minutes(self) -> int:
        return int(os.getenv("SIGNED_URL_EXPIRATION_MINUTES", "60"))

    @property
    def max_conversation_tokens(self) -> int:
        return int(os.getenv("MAX_CONVERSATION_TOKENS", "8000"))

    @property
    def max_decision_tokens(self) -> int:
        return int(os.getenv("MAX_DECISION_TOKENS", "12000"))

# Singleton instance
cloud_config = CloudConfig()
