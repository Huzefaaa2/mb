"""
Azure Blob Storage Container Operations
Handles uploads, downloads, and container management for different purposes
"""

import os
from io import BytesIO
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

# Load environment variables
load_dotenv()

class BlobContainerManager:
    """Manages different blob storage containers for specific purposes"""
    
    # Container types
    CONTAINER_RESUMES = "resumes"
    CONTAINER_TRANSCRIPTS = "transcripts"
    CONTAINER_REPORTS = "analytics-reports"
    CONTAINER_USER_DATA = "user-data"
    CONTAINER_APP_DATA = "application-data"
    
    def __init__(self):
        self.account_name = os.getenv("AZURE_STORAGE_WRITABLE_ACCOUNT_NAME")
        self.account_key = os.getenv("AZURE_STORAGE_WRITABLE_ACCOUNT_KEY")
        self.containers = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize blob service client"""
        try:
            if not self.account_name or not self.account_key:
                print("⚠️  Blob storage credentials not configured")
                return
            
            connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.account_name};"
                f"AccountKey={self.account_key};"
                f"EndpointSuffix=core.windows.net"
            )
            
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            print(f"✓ Connected to storage account: {self.account_name}")
        except Exception as e:
            print(f"✗ Blob storage connection failed: {e}")
    
    def get_container_client(self, container_name):
        """Get or create container client"""
        try:
            if container_name not in self.containers:
                container_client = self.blob_service_client.get_container_client(container_name)
                self.containers[container_name] = container_client
            return self.containers[container_name]
        except Exception as e:
            print(f"✗ Failed to get container client: {e}")
            return None
    
    def upload_resume(self, student_id, file_path):
        """Upload student resume to resumes container"""
        try:
            container = self.get_container_client(self.CONTAINER_RESUMES)
            if not container:
                return False
            
            filename = os.path.basename(file_path)
            blob_name = f"{student_id}/{filename}"
            
            with open(file_path, "rb") as data:
                container.upload_blob(blob_name, data, overwrite=True)
            
            print(f"✓ Resume uploaded: {blob_name}")
            return True
        except Exception as e:
            print(f"✗ Resume upload failed: {e}")
            return False
    
    def upload_transcript(self, transcript_id, transcript_text):
        """Upload speech transcript to transcripts container"""
        try:
            container = self.get_container_client(self.CONTAINER_TRANSCRIPTS)
            if not container:
                return False
            
            blob_name = f"{transcript_id}.txt"
            container.upload_blob(blob_name, transcript_text.encode('utf-8'), overwrite=True)
            
            print(f"✓ Transcript uploaded: {blob_name}")
            return True
        except Exception as e:
            print(f"✗ Transcript upload failed: {e}")
            return False
    
    def upload_report(self, report_id, report_data):
        """Upload analytics report to reports container"""
        try:
            container = self.get_container_client(self.CONTAINER_REPORTS)
            if not container:
                return False
            
            blob_name = f"{report_id}.json"
            container.upload_blob(blob_name, report_data.encode('utf-8'), overwrite=True)
            
            print(f"✓ Report uploaded: {blob_name}")
            return True
        except Exception as e:
            print(f"✗ Report upload failed: {e}")
            return False
    
    def upload_user_data(self, user_id, data_name, data_content):
        """Upload user data to user-data container"""
        try:
            container = self.get_container_client(self.CONTAINER_USER_DATA)
            if not container:
                return False
            
            blob_name = f"{user_id}/{data_name}"
            container.upload_blob(blob_name, data_content, overwrite=True)
            
            print(f"✓ User data uploaded: {blob_name}")
            return True
        except Exception as e:
            print(f"✗ User data upload failed: {e}")
            return False
    
    def download_blob(self, container_name, blob_name):
        """Download blob from specified container"""
        try:
            container = self.get_container_client(container_name)
            if not container:
                return None
            
            blob_client = container.get_blob_client(blob_name)
            download_stream = blob_client.download_blob()
            
            print(f"✓ Blob downloaded: {blob_name}")
            return download_stream.readall()
        except Exception as e:
            print(f"✗ Blob download failed: {e}")
            return None
    
    def list_blobs(self, container_name, prefix=None):
        """List blobs in container"""
        try:
            container = self.get_container_client(container_name)
            if not container:
                return []
            
            blobs = list(container.list_blobs(name_starts_with=prefix))
            return blobs
        except Exception as e:
            print(f"✗ List blobs failed: {e}")
            return []
    
    def delete_blob(self, container_name, blob_name):
        """Delete blob from container"""
        try:
            container = self.get_container_client(container_name)
            if not container:
                return False
            
            container.delete_blob(blob_name)
            print(f"✓ Blob deleted: {blob_name}")
            return True
        except Exception as e:
            print(f"✗ Blob deletion failed: {e}")
            return False

def test_blob_storage():
    """Test blob storage connectivity"""
    manager = BlobContainerManager()
    if manager.blob_service_client:
        print("✓ Blob storage manager initialized")
        return True
    return False

if __name__ == "__main__":
    print("☁️  Testing Azure Blob Storage Containers")
    print("=" * 50)
    
    if test_blob_storage():
        print("\n✅ Blob storage integration ready")
    else:
        print("\n⚠️  Blob storage requires configuration")
