"""
Quick validation script to check all setup requirements
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 14:
        print("✓ Python 3.14+ installed")
        return True
    else:
        print(f"✗ Python 3.14+ required (current: {version.major}.{version.minor})")
        return False

def check_folders():
    """Check folder structure"""
    required_dirs = [
        "mb/pages",
        "mb/components",
        "config",
        "scripts",
        "app/data",
        "data/synthetic"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ missing")
            all_exist = False
    
    return all_exist

def check_files():
    """Check required files"""
    required_files = [
        ".env.example",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "scripts/db_schema.sql",
        "mb/app.py",
        "mb/pages/0_login.py",
        "mb/pages/1_register.py",
        "config/settings.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check .env file"""
    if Path(".env").exists():
        print("✓ .env file exists")
        return True
    else:
        print("⚠ .env file not found (copy from .env.example and fill credentials)")
        return False

def main():
    """Run all checks"""
    print("="*50)
    print("🔍 Magic Bus Compass 360 Setup Validation")
    print("="*50)
    
    print("\n1️⃣  Python Version:")
    python_ok = check_python_version()
    
    print("\n2️⃣  Folder Structure:")
    folders_ok = check_folders()
    
    print("\n3️⃣  Required Files:")
    files_ok = check_files()
    
    print("\n4️⃣  Configuration:")
    env_ok = check_env_file()
    
    print("\n" + "="*50)
    
    if python_ok and folders_ok and files_ok:
        print("✅ All setup checks passed!")
        print("\n📝 Next Steps:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in Azure & Databricks credentials")
        print("  3. Run: pip install -r requirements.txt")
        print("  4. Run: python scripts/generate_synthetic_data.py")
        print("  5. Run: docker-compose up --build")
        print("  6. Or: streamlit run mb/app.py")
    else:
        print("❌ Some checks failed. See above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
