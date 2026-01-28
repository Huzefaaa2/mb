"""
PostgreSQL Database Initialization Module
Handles connection, table creation, and initialization
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection_string():
    """Get PostgreSQL connection string from environment"""
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def init_database():
    """Initialize the PostgreSQL database with schema"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        
        cursor = conn.cursor()
        
        # Read schema from file
        schema_path = Path(__file__).parent.parent / "config" / "db_schema.sql"
        if not schema_path.exists():
            print(f"Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, "r") as f:
            schema = f.read()
        
        # Execute schema
        cursor.execute(schema)
        conn.commit()
        
        print("✓ Database schema initialized successfully")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print("✓ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  Initializing Magic Bus Compass 360 Database")
    print("=" * 50)
    
    if test_connection():
        if init_database():
            print("\n✅ Database initialization complete")
            sys.exit(0)
    
    print("\n❌ Database initialization failed")
    sys.exit(1)
