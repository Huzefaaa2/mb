"""
Azure Blob Storage Handler - Fetch datasets for MagicBus Admin Dashboard
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_blob_data():
    """Fetch data from Azure Blob Storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        # Azure Blob Storage credentials
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        container_name = "usethisone"
        blob_prefix = "apac/"
        
        if not connection_string:
            logger.warning("Azure Storage connection string not found - using sample data")
            return get_sample_datasets()
        
        try:
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(container_name)
            
            blobs = container_client.list_blobs(name_starts_with=blob_prefix)
            datasets = {}
            
            for blob in blobs:
                blob_name = blob.name.replace(blob_prefix, "")
                if blob_name.endswith('.csv') or blob_name.endswith('.json'):
                    try:
                        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
                        blob_data = blob_client.download_blob().readall()
                        datasets[blob_name] = blob_data
                        logger.info(f"Downloaded blob: {blob_name}")
                    except Exception as e:
                        logger.error(f"Error downloading {blob_name}: {e}")
            
            return datasets
        except Exception as e:
            logger.error(f"Error connecting to Blob Storage: {e}")
            return get_sample_datasets()
            
    except ImportError:
        logger.warning("Azure Storage SDK not installed - returning sample data")
        return get_sample_datasets()


def get_sample_datasets():
    """Return sample datasets for demonstration"""
    import json
    
    # Sample student data
    sample_students = {
        "students.json": json.dumps([
            {
                "id": "MB-APAC-2026-001",
                "name": "Raj Kumar",
                "email": "raj@example.com",
                "interests": ["Technology", "AI/ML", "Data Science"],
                "strengths": ["Problem Solving", "Analytical", "Communication"],
                "registration_date": "2026-01-15"
            },
            {
                "id": "MB-APAC-2026-002",
                "name": "Priya Sharma",
                "email": "priya@example.com",
                "interests": ["Business", "Leadership", "Management"],
                "strengths": ["Leadership", "Strategic Thinking", "Teamwork"],
                "registration_date": "2026-01-16"
            },
            {
                "id": "MB-APAC-2026-003",
                "name": "Arjun Patel",
                "email": "arjun@example.com",
                "interests": ["Creative", "Design", "Marketing"],
                "strengths": ["Creativity", "Communication", "Attention to Detail"],
                "registration_date": "2026-01-17"
            },
            {
                "id": "MB-APAC-2026-004",
                "name": "Sneha Gupta",
                "email": "sneha@example.com",
                "interests": ["Technology", "Data Science", "Analytics"],
                "strengths": ["Data Analysis", "Critical Thinking", "Technical Skills"],
                "registration_date": "2026-01-18"
            },
            {
                "id": "MB-APAC-2026-005",
                "name": "Vikram Singh",
                "email": "vikram@example.com",
                "interests": ["Leadership", "Entrepreneurship", "Business"],
                "strengths": ["Initiative", "Leadership", "Risk Management"],
                "registration_date": "2026-01-19"
            }
        ]).encode()
    }
    
    return sample_students


def parse_csv_to_dataframe(csv_data):
    """Parse CSV data to pandas DataFrame"""
    try:
        import pandas as pd
        import io
        
        if isinstance(csv_data, bytes):
            csv_data = csv_data.decode('utf-8')
        
        return pd.read_csv(io.StringIO(csv_data))
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        return None


def parse_json_data(json_data):
    """Parse JSON data"""
    try:
        import json
        
        if isinstance(json_data, bytes):
            json_data = json_data.decode('utf-8')
        
        return json.loads(json_data)
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return None
