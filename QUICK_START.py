#!/usr/bin/env python3
"""
Quick Start Checklist for Magic Bus Compass 360
Run this after cloning to understand setup progression
"""

CHECKLIST = {
    "Phase 1: Pre-Flight Checks": {
        "✅": [
            "Repository cloned from GitHub",
            "Python 3.14+ installed",
            "All 29 files present",
            "Git configured locally"
        ],
        "⏳": []
    },
    
    "Phase 2: Azure Setup (30 min)": {
        "TODO": [
            "Run: azure_setup.ps1 (PowerShell)",
            "This creates: Service Principal, Storage, OpenAI, Speech, KeyVault",
            "Copy generated .env values into .env file",
            "Test Azure connections"
        ]
    },
    
    "Phase 3: Databricks Setup (15 min)": {
        "TODO": [
            "Create Databricks workspace (free tier)",
            "Create catalog 'apac' and schema 'default'",
            "Import CSV tables from Azure Blob",
            "Generate Personal Access Token (PAT)",
            "Add to .env: DATABRICKS_HOST and DATABRICKS_TOKEN"
        ]
    },
    
    "Phase 4: Local Environment (10 min)": {
        "TODO": [
            "pip install -r requirements.txt",
            "python scripts/generate_synthetic_data.py",
            "Verify files in data/synthetic/"
        ]
    },
    
    "Phase 5: Start Application": {
        "TODO": [
            "OPTION A (Docker): docker-compose up --build",
            "OPTION B (Direct): streamlit run mb/app.py",
            "Visit: http://localhost:8501"
        ]
    },
    
    "Phase 6: Test Registration": {
        "TODO": [
            "Register new user",
            "Upload sample resume (PDF/DOCX)",
            "Verify auto-fill works",
            "Check ID card generation",
            "Login with new credentials",
            "Verify PostgreSQL entries"
        ]
    },
    
    "Phase 7: Verify All Systems": {
        "TODO": [
            "PostgreSQL: psql -h localhost -U mb_user -d mb_compass",
            "Streamlit: Load pages without errors",
            "Docker: All containers healthy",
            "Databricks: Test connection",
            "Azure: All credentials working"
        ]
    }
}

FILES_CREATED = {
    "Configuration": [
        ".env.example",
        ".env",
        "config/settings.py",
        "config/secrets.py",
        "config/__init__.py"
    ],
    
    "Database": [
        "scripts/db_schema.sql",
        "scripts/init_db.sh"
    ],
    
    "Backend": [
        "app/data/databricks_loader.py",
        "app/data/__init__.py",
        "app/services/__init__.py",
        "app/components/__init__.py",
        "app/auth/__init__.py"
    ],
    
    "Frontend": [
        "mb/app.py",
        "mb/__init__.py",
        "mb/pages/0_login.py",
        "mb/pages/1_register.py",
        "mb/pages/2_confirmation.py",
        "mb/pages/2_youth_dashboard.py",
        "mb/pages/__init__.py"
    ],
    
    "DevOps": [
        "Dockerfile",
        "docker-compose.yml"
    ],
    
    "Scripts": [
        "scripts/generate_synthetic_data.py",
        "scripts/validate_setup.py"
    ],
    
    "Documentation": [
        "README.md",
        "SETUP_COMPLETE.md",
        "BUILD_SUMMARY.md"
    ],
    
    "Git": [
        ".gitignore"
    ]
}

QUICK_START = """
QUICK START (5 minutes to running)
==================================

1. Fill .env with Azure credentials:
   - Run: .\azure_setup.ps1 (generates credentials)
   - Or manually copy from Azure Portal

2. Add Databricks credentials to .env:
   - DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   - DATABRICKS_TOKEN=dapi2xxxxx

3. Install dependencies:
   pip install -r requirements.txt

4. Generate test data:
   python scripts/generate_synthetic_data.py

5. Start the app:
   docker-compose up --build
   OR
   streamlit run mb/app.py

6. Open browser:
   http://localhost:8501

7. Register a test user (upload any PDF/DOCX)

Done! ✅
"""

TROUBLESHOOTING = """
COMMON ISSUES & SOLUTIONS
=========================

Issue: "ModuleNotFoundError: No module named 'streamlit'"
Solution: pip install -r requirements.txt

Issue: "psycopg2 connection refused"
Solution: 
  - Make sure PostgreSQL is running
  - Check .env has correct POSTGRES_PASSWORD
  - Run: docker-compose up postgres

Issue: ".env file not found"
Solution: 
  - Copy .env.example to .env
  - Fill in your credentials
  - cp .env.example .env

Issue: "Databricks connection failed"
Solution:
  - Check PAT token hasn't expired
  - Verify DATABRICKS_HOST and DATABRICKS_TOKEN in .env
  - Ensure firewall allows connection

Issue: "Database schema not initialized"
Solution:
  - Run: psql -f scripts/db_schema.sql
  - Or restart docker-compose
"""

if __name__ == "__main__":
    print(QUICK_START)
    print("\n" + "="*50)
    print("📝 SETUP CHECKLIST")
    print("="*50)
    
    for phase, items in CHECKLIST.items():
        print(f"\n{phase}")
        if "✅" in items:
            for item in items["✅"]:
                print(f"  ✅ {item}")
        if "⏳" in items:
            for item in items["⏳"]:
                print(f"  ⏳ {item}")
        if "TODO" in items:
            for item in items["TODO"]:
                print(f"  ☐ {item}")
    
    print("\n" + "="*50)
    print("📂 FILES CREATED")
    print("="*50)
    
    total = 0
    for category, files in FILES_CREATED.items():
        print(f"\n{category}: {len(files)} files")
        for file in files:
            print(f"  • {file}")
        total += len(files)
    
    print(f"\nTotal: {total} files")
    
    print("\n" + "="*50)
    print(TROUBLESHOOTING)
