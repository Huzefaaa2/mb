"""
Databricks Integration Module
Handles connection to Databricks SQL and data operations
"""

import os
from dotenv import load_dotenv
from databricks import sql

# Load environment variables
load_dotenv()

class DatabricksConnector:
    """Manages Databricks SQL connections and operations"""
    
    def __init__(self):
        self.host = os.getenv("DATABRICKS_HOST")
        self.token = os.getenv("DATABRICKS_TOKEN")
        self.catalog = os.getenv("DATABRICKS_CATALOG", "apac")
        self.schema = os.getenv("DATABRICKS_SCHEMA", "default")
        self.connection = None
    
    def connect(self):
        """Establish connection to Databricks SQL"""
        try:
            if not self.host or self.host.startswith("<"):
                print("⚠️  Databricks configuration incomplete. Skipping connection.")
                return False
            
            if not self.token or self.token.startswith("<"):
                print("⚠️  Databricks token not configured. Skipping connection.")
                return False
            
            self.connection = sql.connect(
                server_hostname=self.host,
                http_path="/sql/1.0/warehouses/default",
                personal_access_token=self.token,
                catalog=self.catalog,
                schema=self.schema
            )
            print("✓ Databricks SQL connection established")
            return True
        except Exception as e:
            print(f"✗ Databricks connection failed: {e}")
            return False
    
    def execute_query(self, query):
        """Execute a SQL query on Databricks"""
        try:
            if not self.connection:
                print("✗ Databricks connection not established")
                return None
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            return None
    
    def create_table(self, table_name, schema_definition):
        """Create a table in Databricks"""
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema_definition})"
            return self.execute_query(query)
        except Exception as e:
            print(f"✗ Table creation failed: {e}")
            return None
    
    def insert_data(self, table_name, data):
        """Insert data into Databricks table"""
        try:
            if not self.connection:
                print("✗ Databricks connection not established")
                return False
            
            cursor = self.connection.cursor()
            for record in data:
                cursor.execute(f"INSERT INTO {table_name} VALUES ({record})")
            self.connection.commit()
            cursor.close()
            print(f"✓ Data inserted into {table_name}")
            return True
        except Exception as e:
            print(f"✗ Data insertion failed: {e}")
            return False
    
    def close(self):
        """Close Databricks connection"""
        if self.connection:
            self.connection.close()
            print("✓ Databricks connection closed")

def test_databricks_connection():
    """Test Databricks connection"""
    connector = DatabricksConnector()
    if connector.connect():
        connector.close()
        return True
    return False

if __name__ == "__main__":
    print("🔗 Testing Databricks Connection")
    print("=" * 50)
    
    if test_databricks_connection():
        print("\n✅ Databricks integration test passed")
    else:
        print("\n⚠️  Databricks integration requires configuration")
