## Azure CLI Setup & Writable Storage Account Creation

### Prerequisites

Before creating the writable storage account, ensure:

1. **Azure CLI installed**: Download from https://aka.ms/azure-cli
   - Verify: `az --version`

2. **Logged into Azure**:
   ```powershell
   az login
   # This will open a browser for authentication
   ```

3. **Correct subscription access**:
   ```powershell
   # List your subscriptions
   az account list -o table
   
   # Set the BH-IN-Hack For Good subscription (deployment target)
   az account set --subscription "5293e508-036d-433a-a64d-6afe15f3fdc9"
   
   # Verify
   az account show
   ```

### Step 1: Create Writable Storage Account

Run the provided PowerShell script to automatically create the storage account and container in BH-IN-Hack For Good subscription:

```powershell
cd C:\Users\HHusain\mb

# Run the storage account creation script
.\scripts\create_writable_storage.ps1
```

**Expected output:**
```
========================================
Creating Writable Storage Account
========================================
[1/6] Setting Azure subscription context...
[OK] Subscription context set
[2/6] Creating/verifying resource group...
[OK] Resource group created: mb-compass-rg
[3/6] Creating storage account...
[OK] Storage account created: mbcompasswriteXXX
[4/6] Creating blob container...
[OK] Blob container created: application-data
[5/6] Retrieving storage account keys...
[OK] Storage account key retrieved

[6/6] Configuration Summary
========================================

Update your .env file with:

AZURE_STORAGE_WRITABLE_ACCOUNT_NAME=mbcompasswriteXXX
AZURE_STORAGE_WRITABLE_ACCOUNT_KEY=<your-key>
AZURE_STORAGE_WRITABLE_CONTAINER=application-data

========================================
[SUCCESS] Writable storage account ready!
```

### Step 2: Update .env File

1. Open `.env` in the repo root
2. Replace the writable storage placeholders with values from script output:
   ```env
   AZURE_STORAGE_WRITABLE_ACCOUNT_NAME=mbcompasswriteXXX
   AZURE_STORAGE_WRITABLE_ACCOUNT_KEY=your-key-from-output
   AZURE_STORAGE_WRITABLE_CONTAINER=application-data
   ```

3. Optionally customize subscription IDs if different:
   ```env
   AZURE_PRIMARY_SUBSCRIPTION_ID=5293e508-036d-433a-a64d-6afe15f3fdc9
   AZURE_SHARED_SERVICES_SUBSCRIPTION_ID=d8339304-7e56-4567-8b04-52808fdd57b9
   ```

### Step 3: Verify Configuration

Run validation:
```powershell
cd C:\Users\HHusain\mb
python scripts/validate_setup.py
```

Expected output for writable storage configured:
```
✓ All setup checks passed!
✓ Writable storage account configured
✓ Read-only storage account configured
```

### Architecture Overview

#### Storage Account Layout

**Read-Only (BH-SharedServices)**
- Account: `defaultstoragehackathon`
- Container: `usethisone`
- Purpose: Dataset source (Databricks-synced CSVs)
- Access: Entra ID (no keys stored in code)
- Operation: Downloads only

**Writable (BH-IN-Hack For Good)**
- Account: `mbcompasswriteXXX` (created by script)
- Container: `application-data`
- Purpose: Upload resumes, logs, application files
- Access: Account key (stored securely in .env or Key Vault)
- Operations: Upload, delete, archive

#### Data Flow

1. **Read Path (Datasets)**
   ```
   Databricks (apac.default) 
   ← Azure Blob (defaultstoragehackathon/usethisone/apac/*.csv)
   ← DatabricksLoader / BlobStorageManager.read_client
   ```

2. **Write Path (User Uploads)**
   ```
   Student Resume (PDF/DOCX)
   → BlobStorageManager.upload_blob()
   → mbcompasswriteXXX/application-data/resumes/{year}/{student_id}/{filename}
   ← Application archive
   ```

### Runtime Safety Features

The application includes built-in safety checks:

1. **Startup Validation** (`config/startup_checks.py`)
   - Checks read-only storage is configured (REQUIRED)
   - Warns if write storage missing (OPTIONAL but recommended)
   - Blocks app if critical errors found

2. **BlobStorageManager** (`app/data/blob_storage.py`)
   - `upload_blob()` raises `RuntimeError` if write credentials missing
   - `download_blob()` uses read-only credentials only
   - Prevents accidental writes to read-only account

3. **Registration Page** (`mb/pages/1_register.py`)
   - Resume archival is optional (graceful fallback if storage unavailable)
   - Archives to: `resumes/{year}/{student_id}/{filename}`
   - Logs warnings if upload fails

### Troubleshooting

**"Subscription doesn't exist in cloud"**
- Verify subscription ID is correct
- Verify you have access to the subscription
- Run `az account list -o table` to confirm

**"Storage account name already taken"**
- Storage account names must be globally unique
- The script adds random suffix; if conflict, try again or customize name:
  ```powershell
  .\scripts\create_writable_storage.ps1 -StorageAccountName "your-unique-name123"
  ```

**"401 Unauthorized" on upload**
- Check `AZURE_STORAGE_WRITABLE_ACCOUNT_KEY` is correct in .env
- Verify account is in correct subscription
- Try regenerating key in Azure Portal

**Resume archival not working**
- Check logs: `config/startup_checks.py` warnings
- Verify `.env` has `AZURE_STORAGE_WRITABLE_ACCOUNT_NAME` set
- Try running `python scripts/validate_setup.py`

### Next Steps

After setup:

1. **Test Resume Upload** (when student registers)
   - Upload PDF/DOCX resume during registration
   - Check that resume appears in `mbcompasswriteXXX/application-data/resumes/...`

2. **Deploy to Azure Container Apps** (BH-IN-Hack For Good)
   - Use `Dockerfile` and `docker-compose.yml`
   - Reference: Deploy guide in SETUP_COMPLETE.md

3. **Configure Key Vault** (Production)
   - Move storage account keys to Azure Key Vault
   - Use Managed Identity for authentication
   - Update code to use `DefaultAzureCredential`

### File References

- `.env` — Configuration (populate before running)
- `config/settings.py` — Pydantic settings (read/write storage config)
- `config/startup_checks.py` — Startup validation
- `app/data/blob_storage.py` — Blob operations with safety checks
- `mb/pages/1_register.py` — Resume upload integration
- `scripts/create_writable_storage.ps1` — Automation script

---

**Status**: Multi-subscription support implemented ✓  
**Next**: Execute storage account creation script and update .env
