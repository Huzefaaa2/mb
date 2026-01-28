from pydantic import BaseSettings
from typing import Optional
import os

class AzureSettings(BaseSettings):
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    subscription_id: str = ""
    primary_subscription_id: str = ""
    shared_services_subscription_id: str = ""
    
    class Config:
        env_prefix = "AZURE_"

class AzureStorageSettings(BaseSettings):
    # Defaults point to the provided read-only account in BH-SharedServices
    readonly_account_name: str = "defaultstoragehackathon"
    readonly_account_key: str = ""
    readonly_container: str = "usethisone"

    # Writable account should be set to a storage account in BH-IN-Hack For Good
    writable_account_name: Optional[str] = None
    writable_account_key: Optional[str] = None
    writable_container: Optional[str] = None

    region: str = "apac"
    
    @property
    def read_connection_string(self) -> str:
        return f"DefaultEndpointsProtocol=https;AccountName={self.readonly_account_name};AccountKey={self.readonly_account_key};EndpointSuffix=core.windows.net"
    
    @property
    def read_blob_url(self) -> str:
        return f"https://{self.readonly_account_name}.blob.core.windows.net/{self.readonly_container}/{self.region}"

    @property
    def write_connection_string(self) -> str:
        # Prefer explicit writable account; fall back to readonly (legacy behavior) if not set.
        if self.writable_account_name:
            key = self.writable_account_key or ""
            return f"DefaultEndpointsProtocol=https;AccountName={self.writable_account_name};AccountKey={key};EndpointSuffix=core.windows.net"
        return self.read_connection_string
    
    @property
    def write_blob_url(self) -> str:
        if self.writable_account_name and self.writable_container:
            return f"https://{self.writable_account_name}.blob.core.windows.net/{self.writable_container}/{self.region}"
        # Fallback to readonly blob url (no writable configured)
        return self.read_blob_url
    
    class Config:
        env_prefix = "AZURE_STORAGE_"

class AzureOpenAISettings(BaseSettings):
    api_key: str = ""
    endpoint: str = ""
    deployment_gpt35: str = "gpt-35-turbo"
    deployment_gpt4: str = "gpt-4"
    api_version: str = "2024-02-15-preview"
    
    class Config:
        env_prefix = "AZURE_OPENAI_"

class AzureSpeechSettings(BaseSettings):
    key: str = ""
    region: str = "eastus"
    
    class Config:
        env_prefix = "AZURE_SPEECH_"

class DatabricksSettings(BaseSettings):
    host: str = ""
    token: str = ""
    catalog: str = "apac"
    schema: str = "default"
    
    class Config:
        env_prefix = "DATABRICKS_"

class PostgresSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    db: str = "mb_compass"
    user: str = "mb_user"
    password: str = ""
    pool_size: int = 5
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "POSTGRES_"

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    
    azure: AzureSettings = AzureSettings()
    azure_storage: AzureStorageSettings = AzureStorageSettings()
    azure_openai: AzureOpenAISettings = AzureOpenAISettings()
    azure_speech: AzureSpeechSettings = AzureSpeechSettings()
    databricks: DatabricksSettings = DatabricksSettings()
    postgres: PostgresSettings = PostgresSettings()
    
    class Config:
        case_sensitive = False

def get_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        azure=AzureSettings(),
        azure_storage=AzureStorageSettings(),
        azure_openai=AzureOpenAISettings(),
        azure_speech=AzureSpeechSettings(),
        databricks=DatabricksSettings(),
        postgres=PostgresSettings(),
    )

# Global settings instance
settings = get_settings()
