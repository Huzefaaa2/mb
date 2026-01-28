"""
Azure Blob Storage utility with safety checks for read-only vs writable accounts.
Prevents accidental writes to read-only storage and enforces writable storage for uploads.
"""

import logging
from typing import Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, ContainerClient
from config.settings import settings

logger = logging.getLogger(__name__)

class BlobStorageManager:
    """
    Manages Blob Storage operations with safety checks.
    
    - Read operations use the read-only account (defaultstoragehackathon in BH-SharedServices)
    - Write operations require a configured writable account (BH-IN-Hack For Good)
    - Raises errors if write operations are attempted without proper configuration
    """
    
    def __init__(self):
        """Initialize blob storage manager with read and write clients."""
        self._read_client = None
        self._write_client = None
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that read-only account is configured; warn if writable is not."""
        # Check read-only account
        if not settings.azure_storage.readonly_account_name:
            raise ValueError(
                "AZURE_STORAGE_READONLY_ACCOUNT_NAME is not configured. "
                "Cannot read from datasets."
            )
        
        # Warn if writable account not configured
        if not settings.azure_storage.writable_account_name:
            logger.warning(
                "AZURE_STORAGE_WRITABLE_ACCOUNT_NAME is not configured. "
                "Blob write operations will be blocked. "
                "To enable uploads, set writable storage credentials in .env"
            )
    
    @property
    def read_client(self) -> BlobServiceClient:
        """Lazy-load read-only blob client (read from BH-SharedServices)."""
        if self._read_client is None:
            conn_string = settings.azure_storage.read_connection_string
            self._read_client = BlobServiceClient.from_connection_string(conn_string)
        return self._read_client
    
    @property
    def write_client(self) -> Optional[BlobServiceClient]:
        """Lazy-load writable blob client (write to BH-IN-Hack For Good). Returns None if not configured."""
        if not settings.azure_storage.writable_account_name:
            return None
        
        if self._write_client is None:
            conn_string = settings.azure_storage.write_connection_string
            self._write_client = BlobServiceClient.from_connection_string(conn_string)
        return self._write_client
    
    def download_blob(self, blob_name: str, container_name: Optional[str] = None) -> bytes:
        """
        Download a blob from read-only storage.
        
        Args:
            blob_name: Name of the blob to download
            container_name: Container name (defaults to readonly_container)
        
        Returns:
            Blob data as bytes
        
        Raises:
            ValueError: If blob not found or download fails
        """
        container = container_name or settings.azure_storage.readonly_container
        try:
            blob_client = self.read_client.get_blob_client(
                container=container,
                blob=blob_name
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Failed to download blob '{blob_name}' from container '{container}': {e}")
            raise
    
    def upload_blob(
        self,
        blob_name: str,
        data: BinaryIO,
        container_name: Optional[str] = None,
        overwrite: bool = True
    ) -> str:
        """
        Upload a blob to writable storage.
        
        Args:
            blob_name: Name of the blob to create/overwrite
            data: File-like object or bytes to upload
            container_name: Container name (defaults to writable_container)
            overwrite: Whether to overwrite if blob exists
        
        Returns:
            URL of uploaded blob
        
        Raises:
            RuntimeError: If writable storage is not configured
            ValueError: If upload fails
        """
        if not self.write_client:
            raise RuntimeError(
                "AZURE_STORAGE_WRITABLE_ACCOUNT_NAME is not configured. "
                "Cannot upload to Blob Storage. "
                "Please configure writable storage in .env and try again."
            )
        
        container = container_name or settings.azure_storage.writable_container
        if not container:
            raise ValueError(
                "AZURE_STORAGE_WRITABLE_CONTAINER is not configured. "
                "Cannot determine upload destination."
            )
        
        try:
            blob_client = self.write_client.get_blob_client(
                container=container,
                blob=blob_name
            )
            blob_client.upload_blob(data, overwrite=overwrite)
            
            blob_url = f"{settings.azure_storage.write_blob_url}/{blob_name}"
            logger.info(f"Blob uploaded successfully: {blob_url}")
            return blob_url
        
        except Exception as e:
            logger.error(f"Failed to upload blob '{blob_name}': {e}")
            raise
    
    def list_blobs(self, container_name: Optional[str] = None, prefix: str = "") -> list:
        """
        List blobs in read-only container.
        
        Args:
            container_name: Container name (defaults to readonly_container)
            prefix: Filter blobs by prefix
        
        Returns:
            List of blob names
        """
        container = container_name or settings.azure_storage.readonly_container
        try:
            container_client = self.read_client.get_container_client(container)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list blobs in '{container}': {e}")
            raise
    
    def delete_blob(self, blob_name: str, container_name: Optional[str] = None) -> None:
        """
        Delete a blob from writable storage.
        
        Args:
            blob_name: Name of blob to delete
            container_name: Container name (defaults to writable_container)
        
        Raises:
            RuntimeError: If writable storage not configured
            ValueError: If deletion fails
        """
        if not self.write_client:
            raise RuntimeError(
                "AZURE_STORAGE_WRITABLE_ACCOUNT_NAME is not configured. "
                "Cannot delete from Blob Storage."
            )
        
        container = container_name or settings.azure_storage.writable_container
        try:
            blob_client = self.write_client.get_blob_client(
                container=container,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Blob deleted: {blob_name}")
        except Exception as e:
            logger.error(f"Failed to delete blob '{blob_name}': {e}")
            raise


# Global instance
_blob_manager = None

def get_blob_storage_manager() -> BlobStorageManager:
    """Get or create global blob storage manager instance."""
    global _blob_manager
    if _blob_manager is None:
        _blob_manager = BlobStorageManager()
    return _blob_manager
