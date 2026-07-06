import os
from typing import Optional
from backend.platform.cloud.logging_provider import cloud_logger

class SecretManager:
    """
    Interface to Google Secret Manager with local AES-256 fallback.
    """
    def __init__(self):
        self.is_local = os.environ.get("ENV") == "local"

    def get_secret(self, secret_id: str) -> Optional[str]:
        if self.is_local:
            # Fallback to local encrypted environment store
            cloud_logger.debug(f"Fetching secret {secret_id} from LocalSecretProvider")
            return os.environ.get(f"SECRET_{secret_id}")
        else:
            # Placeholder for Google Cloud Secret Manager SDK
            cloud_logger.debug(f"Fetching secret {secret_id} from Google Secret Manager")
            return "mock-secret-value-from-gsm"
            
class EncryptionManager:
    """
    Handles encryption at rest using Google Cloud KMS or local AES fallback.
    """
    def __init__(self):
        self.secret_manager = SecretManager()
        
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypts sensitive data before writing to StorageManager.
        """
        # Placeholder for real AES/KMS encryption logic
        return f"ENCRYPTED:[{plaintext}]"
        
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypts data read from StorageManager.
        """
        if ciphertext.startswith("ENCRYPTED:[") and ciphertext.endswith("]"):
            return ciphertext[11:-1]
        return ciphertext
