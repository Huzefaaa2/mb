# 🚀 Magic Bus Compass 360 - Setup & Configuration Guide

## ✅ Installation Checklist

### 1. Environment Configuration (.env)

Create/update `.env` file in project root with:

```env
# ===== EXISTING (Azure OpenAI) =====
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_GPT35=gpt-35-turbo

# ===== NEW (JobGPT - SerpAPI) =====
# Get key from: https://serpapi.com
SERPAPI_KEY=your_serpapi_api_key

# ===== NEW (Azure Storage - Optional) =====
# For Blob Storage access
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# ===== NEW (Admin Dashboard) =====
ADMIN_PASSWORD=your_secure_admin_password
```

### 2. Install Additional Dependencies

If not already installed:

```bash
cd c:\Users\HHusain\mb
.venv\Scripts\pip install serpapi azure-storage-blob --upgrade
```

### 3. Database Initialization

New tables auto-created on first access:
- `user_badges` - Achievement tracking
- `learning_streaks` - Streak management

No manual migration needed!

---

## 🎮 Feature Configuration

### Gamification System

**Location:** `mb/pages/gamification.py`

**Configuration Options:**
```python
# Badge criteria (lines 46-65)
# Modify thresholds for different badge levels

# Motivational messages (line 250+)
# Customize motivation text based on milestones
```

**To customize badges:**
1. Edit `gamification.py`
2. Modify `badge_criteria` list
3. Change completion thresholds
4. Restart app: `streamlit run mb/app.py`

---

### JobGPT Configuration

**Job Search (SerpAPI):**
- Get free API key at: https://serpapi.com/
- Add `SERPAPI_KEY` to .env
- App uses demo jobs if key missing

**Resume Matching:**
- Uses Azure OpenAI automatically
- No additional config needed
- Requires `AZURE_OPENAI_*` credentials

**Interview Prep:**
- Customizable by experience level
- Default: 5 questions per session
- Edit `interview_bot.py` to modify count

---

### Admin Dashboard

**Access:**
1. Go to Sidebar → "📈 MagicBus Admin"
2. Enter `ADMIN_PASSWORD` from .env
3. Full access to analytics

**Password Change:**
```bash
# Update .env
ADMIN_PASSWORD=new_secure_password

# Restart app
```

**Data Access:**
- Reads from SQLite database directly
- No additional permissions needed
- Azure Blob Storage optional (demo data used if unavailable)

---

## 📊 Database Schema

### New Tables

#### `user_badges`
```sql
CREATE TABLE user_badges (
    badge_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_name TEXT NOT NULL,
    badge_description TEXT,
    badge_icon TEXT,
    earned_date TIMESTAMP,
    UNIQUE(user_id, badge_name),
    FOREIGN KEY (user_id) REFERENCES mb_users(user_id)
)
```

#### `learning_streaks`
```sql
CREATE TABLE learning_streaks (
    streak_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    current_streak INTEGER,
    longest_streak INTEGER,
    last_activity_date TIMESTAMP,
    UNIQUE(user_id),
    FOREIGN KEY (user_id) REFERENCES mb_users(user_id)
)
```

---

## 🔑 API Keys & Credentials

### Required APIs

| API | Purpose | Where to Get | Free Tier |
|-----|---------|-------------|-----------|
| **Azure OpenAI** | AI recommendations, cover letters, interview prep | Azure Portal | $5 free credit |
| **SerpAPI** | Job search | https://serpapi.com | 100 free searches/month |

### Optional APIs

| Service | Purpose | Status |
|---------|---------|--------|
| **Azure Blob Storage** | Load student datasets | Optional - demo data used if unavailable |

---

## 🧪 Testing Checklist

### Test Gamification
- [ ] Login as student
- [ ] Start a learning module
- [ ] Check if "First Step" badge appears
- [ ] Complete a module
- [ ] Verify "Module Completer" badge
- [ ] Check streak counter

### Test JobGPT
- [ ] Go to "JobGPT" section
- [ ] Search for jobs (demo data should appear)
- [ ] Paste sample resume
- [ ] Click "Analyze Match"
- [ ] Generate cover letter
- [ ] Generate interview questions

### Test Admin Dashboard
- [ ] Sidebar → "📈 MagicBus Admin"
- [ ] Enter admin password
- [ ] View Overview tab
- [ ] Check Student Analytics
- [ ] Generate a Report
- [ ] Verify AI Recommendations

---

## 🚀 Deployment Guide

### Local Testing
```bash
cd c:\Users\HHusain\mb
.venv\Scripts\streamlit run mb/app.py
```

### Production Deployment (Streamlit Cloud)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add gamification, JobGPT, admin dashboard"
   git push
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to: https://share.streamlit.io
   - Connect GitHub repository
   - Deploy with secrets:
     ```
     AZURE_OPENAI_API_KEY=***
     SERPAPI_KEY=***
     ADMIN_PASSWORD=***
     ```

3. **Azure Container Apps:**
   ```bash
   # Build image
   docker build -t magicbus:latest .
   
   # Deploy
   az containerapp create --resource-group mb-group \
     --name magicbus-app \
     --image magicbus:latest
   ```

---

## 📋 Maintenance Tasks

### Weekly
- [ ] Monitor admin dashboard for system health
- [ ] Check badge/streak distribution
- [ ] Review job search usage

### Monthly
- [ ] Backup SQLite database
- [ ] Review and update AI recommendations
- [ ] Check Azure costs
- [ ] Analyze student engagement metrics

### Quarterly
- [ ] Update AI prompts for recommendations
- [ ] Add new badges/gamification elements
- [ ] Refresh course recommendations
- [ ] Plan new features with stakeholders

---

## 🐛 Troubleshooting

### JobGPT Not Working
**Issue:** Job search returns no results
**Solution:**
1. Check `SERPAPI_KEY` in .env
2. Verify API quota: https://serpapi.com/account
3. App auto-uses demo data if API fails

### Admin Dashboard Password Not Working
**Issue:** "Invalid credentials" error
**Solution:**
1. Check `ADMIN_PASSWORD` in .env
2. Ensure .env is in project root
3. Restart app after changing .env

### Badges Not Appearing
**Issue:** Completed module but no badge
**Solution:**
1. Refresh browser
2. Check module status in database:
   ```sql
   SELECT * FROM learning_modules WHERE status='completed';
   ```
3. Manually award badge:
   ```sql
   INSERT INTO user_badges (user_id, badge_name, badge_description, badge_icon)
   VALUES (2, 'Module Completer', 'Completed your first module', '✅');
   ```

### Azure OpenAI Connection Failed
**Issue:** "Could not generate recommendations"
**Solution:**
1. Verify credentials in .env:
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT_GPT35`
2. Test connection:
   ```python
   from openai import AzureOpenAI
   client = AzureOpenAI(api_key=..., azure_endpoint=..., api_version=...)
   # Should not raise error
   ```

---

## 📞 Support

For issues, questions, or feature requests:
1. Check this documentation
2. Review error logs in terminal
3. Check Azure Portal for quota/billing issues
4. Open GitHub issue with error details

---

## 📜 License & Attribution

- **JobGPT Core:** Based on personal GitHub project
- **Gamification:** Custom implementation
- **Admin Dashboard:** Custom enterprise features
- **License:** Follows main project license

---

**Last Updated:** January 29, 2026
**Version:** 2.0
