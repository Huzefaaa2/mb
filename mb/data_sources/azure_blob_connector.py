"""
Azure Blob Storage Connector
Retrieves datasets from Azure Blob Storage for Decision Intelligence Dashboard
Data Source: https://defaultstoragehackathon.blob.core.windows.net/usethisone/apac
"""

import pandas as pd
import io
import logging
from pathlib import Path
from typing import Optional, Dict, List
from azure.storage.blob import BlobServiceClient, BlobClient
import os

logger = logging.getLogger(__name__)


class AzureBlobConnector:
    """Connects to Azure Blob Storage and retrieves datasets"""
    
    def __init__(self):
        # Azure Blob Storage configuration
        self.account_name = "defaultstoragehackathon"
        self.container_name = "usethisone"
        self.folder_path = "apac"
        self.connection_string = os.getenv(
            "AZURE_STORAGE_CONNECTION_STRING",
            "DefaultEndpointsProtocol=https;AccountName=defaultstoragehackathon;AccountKey=default;EndpointSuffix=core.windows.net"
        )
        
        # Initialize blob client
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            logger.info("✅ Azure Blob Storage connected")
        except Exception as e:
            logger.warning(f"⚠️ Azure connection failed: {e}. Using local fallback.")
            self.blob_service_client = None
            self.container_client = None
    
    def list_available_datasets(self) -> List[str]:
        """List all CSV files available in the blob folder"""
        if not self.container_client:
            return []
        
        try:
            blobs = self.container_client.list_blobs(name_starts_with=f"{self.folder_path}/")
            files = [blob.name.split('/')[-1] for blob in blobs if blob.name.endswith('.csv')]
            return sorted(list(set(files)))
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            return []
    
    def get_dataset(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieve a dataset from Azure Blob Storage
        
        Args:
            table_name: Name of the CSV file (e.g., 'students', 'learning_modules')
            limit: Optional row limit for sampling
        
        Returns:
            DataFrame with the dataset
        """
        if not self.container_client:
            logger.warning(f"No Azure connection. Returning empty DataFrame for {table_name}")
            return pd.DataFrame()
        
        try:
            blob_path = f"{self.folder_path}/{table_name}.csv"
            blob_client = self.container_client.get_blob_client(blob_path)
            
            # Download blob content
            blob_data = blob_client.download_blob()
            csv_content = blob_data.readall()
            
            # Read CSV into DataFrame
            df = pd.read_csv(io.BytesIO(csv_content))
            
            if limit:
                df = df.head(limit)
            
            logger.info(f"✅ Loaded {table_name}: {len(df)} rows, {len(df.columns)} columns")
            return df
        
        except Exception as e:
            logger.error(f"Error loading {table_name}: {e}")
            return pd.DataFrame()
    
    def get_multiple_datasets(self, table_names: List[str]) -> Dict[str, pd.DataFrame]:
        """Load multiple datasets at once"""
        datasets = {}
        for table_name in table_names:
            datasets[table_name] = self.get_dataset(table_name)
        return datasets
    
    # ========================
    # CORE DATASETS
    # ========================
    
    def get_students(self) -> pd.DataFrame:
        """Get students dataset"""
        return self.get_dataset("students")
    
    def get_learning_modules(self) -> pd.DataFrame:
        """Get learning modules dataset"""
        return self.get_dataset("learning_modules")
    
    def get_student_progress(self) -> pd.DataFrame:
        """Get student progress/module completion data"""
        return self.get_dataset("student_progress")
    
    def get_career_interests(self) -> pd.DataFrame:
        """Get career interests data"""
        return self.get_dataset("career_interests")
    
    def get_career_pathways(self) -> pd.DataFrame:
        """Get career pathway definitions"""
        return self.get_dataset("career_pathways")
    
    def get_student_achievements(self) -> pd.DataFrame:
        """Get student achievements/badges"""
        return self.get_dataset("student_achievements")
    
    def get_student_skills(self) -> pd.DataFrame:
        """Get student skill assessments"""
        return self.get_dataset("student_skills")
    
    def get_skills(self) -> pd.DataFrame:
        """Get skill definitions"""
        return self.get_dataset("skills")
    
    def get_quiz_attempts(self) -> pd.DataFrame:
        """Get quiz attempt data"""
        return self.get_dataset("quiz_attempts")
    
    def get_daily_challenges(self) -> pd.DataFrame:
        """Get daily challenges data"""
        return self.get_dataset("daily_challenges")
    
    def get_points_ledger(self) -> pd.DataFrame:
        """Get points/gamification ledger"""
        return self.get_dataset("points_ledger")
    
    def get_schools(self) -> pd.DataFrame:
        """Get school information"""
        return self.get_dataset("schools")
    
    def get_teachers(self) -> pd.DataFrame:
        """Get teacher information"""
        return self.get_dataset("teachers")
    
    def get_user_sessions(self) -> pd.DataFrame:
        """Get user session data for engagement tracking"""
        return self.get_dataset("user_sessions")
    
    def get_notifications(self) -> pd.DataFrame:
        """Get notifications data"""
        return self.get_dataset("notifications")
    
    # ========================
    # QUIZ & ASSESSMENT DATA
    # ========================
    
    def get_quizzes(self) -> pd.DataFrame:
        """Get quiz definitions"""
        return self.get_dataset("quizzes")
    
    def get_quiz_questions(self) -> pd.DataFrame:
        """Get quiz questions"""
        return self.get_dataset("quiz_questions")
    
    def get_quiz_responses(self) -> pd.DataFrame:
        """Get individual quiz responses"""
        return self.get_dataset("quiz_responses")
    
    # ========================
    # SAFETY SCENARIOS
    # ========================
    
    def get_safety_scenarios(self) -> pd.DataFrame:
        """Get safety scenario data"""
        return self.get_dataset("safety_scenarios")
    
    def get_scenario_responses(self) -> pd.DataFrame:
        """Get safety scenario responses"""
        return self.get_dataset("scenario_responses")
    
    # ========================
    # DATA QUALITY CHECKS
    # ========================
    
    def validate_dataset(self, df: pd.DataFrame, table_name: str) -> Dict[str, any]:
        """Validate dataset quality"""
        validation = {
            "table_name": table_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_count": df.isnull().sum().sum(),
            "null_by_column": df.isnull().sum().to_dict(),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }
        return validation
    
    def get_health_report(self) -> Dict[str, any]:
        """Get overall data source health"""
        core_tables = [
            "students", "learning_modules", "student_progress",
            "career_interests", "student_achievements", "quiz_attempts"
        ]
        
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "connection_status": "connected" if self.container_client else "disconnected",
            "available_datasets": self.list_available_datasets(),
            "tables_checked": {}
        }
        
        for table in core_tables:
            try:
                df = self.get_dataset(table, limit=1)
                report["tables_checked"][table] = {
                    "status": "available" if len(df) > 0 else "empty",
                    "row_count": len(df),
                    "columns": len(df.columns) if len(df) > 0 else 0
                }
            except Exception as e:
                report["tables_checked"][table] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return report


# ========================
# SINGLETON INSTANCE
# ========================

_connector_instance = None


def get_blob_connector() -> AzureBlobConnector:
    """Get singleton connector instance"""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = AzureBlobConnector()
    return _connector_instance


def test_connection():
    """Test Azure Blob Storage connection"""
    connector = get_blob_connector()
    health = connector.get_health_report()
    
    print("\n" + "="*60)
    print("AZURE BLOB STORAGE CONNECTION TEST")
    print("="*60)
    print(f"Status: {health['connection_status'].upper()}")
    print(f"Available Datasets: {len(health['available_datasets'])}")
    
    for table, status in health['tables_checked'].items():
        print(f"\n  {table}: {status['status']}")
        if status['status'] == "available":
            print(f"    - Rows: {status['row_count']}")
            print(f"    - Columns: {status['columns']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_connection()
