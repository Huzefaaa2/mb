"""
Integration Test Module
Tests all Azure service integrations
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.databricks_connector import test_databricks_connection
from app.integrations.speech_to_text import test_speech_service
from app.integrations.blob_container_manager import test_blob_storage
from scripts.init_db import test_connection as test_postgres

def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("🔧 Magic Bus Compass 360 - Integration Tests")
    print("="*60 + "\n")
    
    results = {}
    
    # Test PostgreSQL
    print("1️⃣  Testing PostgreSQL...")
    results['PostgreSQL'] = test_postgres()
    
    # Test Blob Storage
    print("\n2️⃣  Testing Blob Storage...")
    results['Blob Storage'] = test_blob_storage()
    
    # Test Speech to Text
    print("\n3️⃣  Testing Speech to Text...")
    results['Speech to Text'] = test_speech_service()
    
    # Test Databricks
    print("\n4️⃣  Testing Databricks...")
    results['Databricks'] = test_databricks_connection()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Integration Test Results")
    print("="*60)
    
    for service, status in results.items():
        status_icon = "✓" if status else "✗"
        print(f"{status_icon} {service}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All integration tests passed!")
    else:
        print("\n⚠️  Some integrations require configuration")
    
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
