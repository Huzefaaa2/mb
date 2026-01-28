# Quick Reference: Multi-Subscription Storage Setup

## The Challenge
- **Read-only storage** in BH-SharedServices (`defaultstoragehackathon`)
- **Writable storage** needed in BH-IN-Hack For Good subscription
- **Solution**: Application routes reads to one account, writes to another

## What's Implemented

### Files Changed
```
config/settings.py          ← Added dual storage config
app/data/blob_storage.py    ← NEW: Safety-enforced blob manager
config/startup_checks.py    ← NEW: Config validation on startup
mb/app.py                   ← Added startup checks
mb/pages/1_register.py      ← Added resume archival
scripts/create_writable_storage.ps1  ← NEW: Automation script
.env                        ← Restructured for clarity
```

### Storage Architecture
```
┌─────────────────────────────────────────────────────────────┐
│  Magic Bus Compass 360 Application                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Read Data]              [Write Data]                     │
│  download_blob()          upload_blob()                    │
│         ↓                        ↓                         │
│  ┌──────────────┐         ┌──────────────┐               │
│  │ Read-Only    │         │ Writable     │               │
│  │ Account      │         │ Account      │               │
│  │ (BH-Svc)    │         │ (BH-HforG)  │               │
│  │ default...  │         │ mcompass... │               │
│  │ usethisone/ │         │ app-data/   │               │
│  │ apac/*.csv  │         │ resumes/... │               │
│  └──────────────┘         └──────────────┘               │
│  Sub: SHARED-SVC         Sub: BH-IN-HACK-FOR-GOOD       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Execution Checklist

### Phase 1: Azure Setup (5 min)
- [ ] Run `az login` → authenticate
- [ ] Verify: `az account show` → should be BH-IN-Hack For Good
- [ ] Execute: `.\scripts\create_writable_storage.ps1`
- [ ] Copy output → storage account name, key, container

### Phase 2: .env Configuration (2 min)
- [ ] Open `.env` in repo root
- [ ] Paste into `.env`:
  ```
  AZURE_STORAGE_WRITABLE_ACCOUNT_NAME=<from-script>
  AZURE_STORAGE_WRITABLE_ACCOUNT_KEY=<from-script>
  AZURE_STORAGE_WRITABLE_CONTAINER=application-data
  ```
- [ ] Save file

### Phase 3: Verification (2 min)
- [ ] Run: `python scripts/validate_setup.py`
- [ ] Look for: "Writable storage account configured ✓"
- [ ] All checks passed ✓

### Phase 4: Test (5 min)
- [ ] Run: `streamlit run mb/app.py`
- [ ] Navigate to Registration page
- [ ] Upload PDF/DOCX resume
- [ ] Complete registration
- [ ] Verify resume appears in Azure Portal:
  - Storage account: `mbcompasswriteXXX`
  - Container: `application-data`
  - Path: `resumes/2026/{student_id}/{filename}`

## Subscription IDs

| Subscription | Purpose | ID |
|---|---|---|
| BH-SharedServices | Read-only data (datasets) | `d8339304-7e56-4567-8b04-52808fdd57b9` |
| BH-IN-Hack For Good | Writable (app deployments) | `5293e508-036d-433a-a64d-6afe15f3fdc9` |

## Key Code Paths

### Reading Data (Read-Only Account)
```python
from app.data.blob_storage import get_blob_storage_manager

mgr = get_blob_storage_manager()
data = mgr.download_blob("apac/students.csv")  # Reads from readonly
```

### Writing Data (Writable Account)
```python
from app.data.blob_storage import get_blob_storage_manager

mgr = get_blob_storage_manager()
try:
    url = mgr.upload_blob(
        "resumes/2026/MB-APAC-2026-ABC123/resume.pdf",
        resume_file
    )
except RuntimeError as e:
    # Writable storage not configured
    print(f"Upload failed: {e}")
```

### Configuration Validation
```python
from config.startup_checks import check_azure_configuration

errors, warnings = check_azure_configuration()
if errors:
    print("CRITICAL CONFIG ERRORS:")
    for e in errors:
        print(f"  - {e}")
    exit(1)
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| "Subscription doesn't exist" | Run `az account set --subscription <id>` |
| "Storage account name taken" | Run script again (random suffix) or use custom name |
| "401 Unauthorized on upload" | Check account key in .env (regenerate if needed) |
| "Resume not archiving" | Run `python scripts/validate_setup.py` → check warnings |

## Documentation Links

- **Full Setup Guide**: `docs/AZURE_SETUP_WRITABLE_STORAGE.md`
- **Implementation Details**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Config Reference**: `config/settings.py`
- **Blob Manager API**: `app/data/blob_storage.py`

## Support

All configuration is documented in `.env.example` comments. Files include detailed docstrings.

Questions? See `docs/AZURE_SETUP_WRITABLE_STORAGE.md` → Troubleshooting section.

---

**Status**: Implementation complete, committed to GitHub ✓  
**Next**: Execute Phase 1-2 (Azure setup & .env update)
