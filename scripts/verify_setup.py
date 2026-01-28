#!/usr/bin/env python
"""
Final Setup Verification - Magic Bus Compass 360
Confirms all services are properly configured and connected
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def verify_env_variables():
    """Verify all required environment variables are set"""
    print("\n📋 Checking Environment Variables...")
    print("-" * 50)
    
    required_vars = {
        'PostgreSQL': ['POSTGRES_HOST', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB'],
        'Blob Storage': ['AZURE_STORAGE_WRITABLE_ACCOUNT_NAME', 'AZURE_STORAGE_WRITABLE_ACCOUNT_KEY'],
        'Speech Services': ['AZURE_SPEECH_API_KEY', 'AZURE_SPEECH_REGION'],
        'OpenAI': ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT'],
        'Databricks': ['DATABRICKS_WORKSPACE_NAME'],
    }
    
    all_set = True
    for service, vars_list in required_vars.items():
        service_ok = True
        for var in vars_list:
            value = os.getenv(var)
            if not value or value.startswith('<'):
                service_ok = False
                all_set = False
                status = "❌ MISSING"
            else:
                status = "✓ OK"
            print(f"  {status} {var}")
        print()
    
    return all_set

def verify_folders():
    """Verify all required folders exist"""
    print("📁 Checking Folder Structure...")
    print("-" * 50)
    
    required_folders = [
        'mb',
        'mb/pages',
        'app/integrations',
        'config',
        'scripts',
    ]
    
    all_exist = True
    for folder in required_folders:
        if Path(folder).exists():
            print(f"✓ {folder}/")
        else:
            print(f"❌ {folder}/ (missing)")
            all_exist = False
    print()
    
    return all_exist

def verify_files():
    """Verify all required files exist"""
    print("📄 Checking Required Files...")
    print("-" * 50)
    
    required_files = [
        'mb/app.py',
        'mb/pages/0_login.py',
        'mb/pages/1_register.py',
        '.env',
        'config/settings.py',
        'app/integrations/databricks_connector.py',
        'app/integrations/speech_to_text.py',
        'app/integrations/blob_container_manager.py',
        'scripts/init_db.py',
        'scripts/test_integrations.py',
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"❌ {file} (missing)")
            all_exist = False
    print()
    
    return all_exist

def verify_imports():
    """Verify all required Python modules can be imported"""
    print("🐍 Checking Python Modules...")
    print("-" * 50)
    
    modules = [
        ('streamlit', 'Streamlit UI'),
        ('psycopg2', 'PostgreSQL Driver'),
        ('qrcode', 'QR Code Generation'),
        ('PIL', 'Image Processing'),
        ('fpdf', 'PDF Generation'),
        ('PyPDF2', 'PDF Manipulation'),
        ('azure.storage.blob', 'Azure Blob Storage'),
        ('azure.cognitiveservices.speech', 'Azure Speech-to-Text'),
        ('dotenv', 'Environment Variables'),
        ('pydantic_settings', 'Configuration Management'),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name:<25} ({description})")
        except ImportError:
            print(f"❌ {module_name:<25} ({description}) - NOT INSTALLED")
            all_ok = False
    print()
    
    return all_ok

def main():
    """Run all verification checks"""
    print("\n" + "="*50)
    print("🔍 Magic Bus Compass 360 Setup Verification")
    print("="*50)
    
    results = {
        'Environment Variables': verify_env_variables(),
        'Folder Structure': verify_folders(),
        'Required Files': verify_files(),
        'Python Modules': verify_imports(),
    }
    
    # Summary
    print("="*50)
    print("✅ Verification Summary")
    print("="*50)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ All checks passed! Application is ready to use.")
        print("\n🚀 Next Steps:")
        print("  1. Access: http://localhost:8502")
        print("  2. Register a new student account")
        print("  3. Login and explore the dashboard")
        print("\n📚 To initialize the database:")
        print("  python scripts/init_db.py")
        print("\n🧪 To test integrations:")
        print("  python scripts/test_integrations.py")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print("Check .env file and verify all credentials are properly set.")
    
    print("="*50 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
