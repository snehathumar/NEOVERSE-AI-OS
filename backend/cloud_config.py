import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CloudConfig:
    """
    Central Configuration Module for Google Cloud Services.
    Reads credentials and project details securely from environment variables.
    """
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CloudConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Retrieve project settings from .env
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # We don't initialize the actual clients here to avoid crashing 
        # if the .env file or credentials aren't set up yet. 
        # The clients will be lazily loaded when requested.
        self._firestore_client = None
        self._bigquery_client = None
        self._storage_client = None

    def _validate_credentials(self):
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID is missing in .env")
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is missing or file does not exist")

    def get_firestore_client(self):
        """Returns a reusable Google Cloud Firestore client."""
        if self._firestore_client is None:
            self._validate_credentials()
            from google.cloud import firestore
            self._firestore_client = firestore.Client(project=self.project_id)
        return self._firestore_client

    def get_bigquery_client(self):
        """Returns a reusable Google Cloud BigQuery client."""
        if self._bigquery_client is None:
            self._validate_credentials()
            from google.cloud import bigquery
            self._bigquery_client = bigquery.Client(project=self.project_id)
        return self._bigquery_client

    def get_storage_client(self):
        """Returns a reusable Google Cloud Storage client."""
        if self._storage_client is None:
            self._validate_credentials()
            from google.cloud import storage
            self._storage_client = storage.Client(project=self.project_id)
        return self._storage_client

# Singleton instance to be imported by other modules
cloud_config = CloudConfig()
