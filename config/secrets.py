import os
from typing import Optional
from config.settings import get_settings

class SecretsManager:
    """Manage secrets from .env (dev) or Azure Key Vault (prod)."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.settings = get_settings()
    
    def get_azure_credential(self):
        """Get Azure credential object for auth."""
        try:
            from azure.identity import DefaultAzureCredential, ClientSecretCredential
            
            if self.environment == "production":
                # Use managed identity on Azure
                return DefaultAzureCredential()
            else:
                # Use service principal for local dev
                return ClientSecretCredential(
                    tenant_id=self.settings.azure.tenant_id,
                    client_id=self.settings.azure.client_id,
                    client_secret=self.settings.azure.client_secret,
                )
        except ImportError:
            print("Azure SDK not installed")
            return None
    
    def get_key_vault_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from Azure Key Vault (if prod)."""
        if self.environment == "production":
            try:
                from azure.keyvault.secrets import SecretClient
                
                vault_url = f"https://mb-kv-{self.environment}.vault.azure.net/"
                credential = self.get_azure_credential()
                client = SecretClient(vault_url=vault_url, credential=credential)
                
                return client.get_secret(secret_name).value
            except Exception as e:
                print(f"Error retrieving secret {secret_name}: {e}")
                return None
        else:
            # For dev, secrets are in .env
            return os.getenv(secret_name.upper())

secrets_manager = SecretsManager()
