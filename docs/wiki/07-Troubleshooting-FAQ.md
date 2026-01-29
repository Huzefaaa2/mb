# Troubleshooting & FAQ

## Frequently Asked Questions (FAQ)

### General Questions

#### Q: What is the Magic Bus platform?
**A:** Magic Bus is a comprehensive youth employment and skills platform that:
- Provides personalized learning modules
- Tracks career development and sector fit
- Collects employer feedback for continuous improvement
- Gamifies learning with badges and points
- Connects youth with employment opportunities

#### Q: Who can use the platform?
**A:** The platform is designed for:
- **Students**: Youth participants in the Magic Bus program
- **Instructors**: Content creators and learning coordinators
- **Admins**: Platform administrators and data analysts
- **Employers**: Partners providing placement feedback

#### Q: How do I create an account?
**A:** 
1. Go to the login page
2. Click "Register"
3. Enter your email and create a password
4. Complete your profile information
5. Verify your email address
6. You're ready to start!

---

### Technical Questions

#### Q: What are the system requirements?
**A:**
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Internet**: Minimum 2 Mbps connection
- **Device**: Desktop, tablet, or mobile
- **Storage**: 50 MB available space

#### Q: Which Python version is required?
**A:** Python 3.11 or higher. Install from: https://www.python.org/downloads/

#### Q: How do I install dependencies?
**A:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Mac/Linux

# Install requirements
pip install -r requirements-py311.txt
```

#### Q: How do I start the application locally?
**A:**
```bash
# Method 1: Direct Streamlit
streamlit run app/app.py

# Method 2: Docker Compose
docker-compose up -d

# Application opens at http://localhost:8501
```

#### Q: I'm getting "Port 8501 already in use" error
**A:**
```bash
# Use a different port
streamlit run app/app.py --server.port 8502

# Or find and kill the process
lsof -ti:8501 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8501    # Windows
```

---

### Data & Database

#### Q: How is my data stored?
**A:** 
- **Local**: SQLite database in `mb/data/mb_app.db`
- **Cloud**: Azure SQL Database (production)
- **Files**: Azure Blob Storage for documents
- **Analytics**: Databricks for feature engineering

#### Q: Is my data secure?
**A:** 
- Passwords: Bcrypt hashing (cannot be reversed)
- Transmission: HTTPS/SSL encryption
- Storage: Encrypted at rest
- Access: Role-based access control (RBAC)

#### Q: How do I back up my data?
**A:**
```bash
# Local backup
cp mb/data/mb_app.db backups/mb_app_backup.db

# Azure backup (automated daily)
# Manual backup available in Azure Portal
```

#### Q: Can I export my data?
**A:** Yes:
1. Log in as admin
2. Navigate to Analytics → Export
3. Select date range and format (CSV, Excel, PDF)
4. Download file

#### Q: How long is data retained?
**A:**
- Active accounts: Retained indefinitely
- Deleted accounts: 90-day grace period, then permanently deleted
- Survey responses: Retained for 7 years
- Log files: Retained for 30 days

---

### Surveys & Feedback

#### Q: Why am I being asked to complete surveys?
**A:** Surveys help:
- Employers understand student capabilities
- Students get professional feedback
- Magic Bus improve the program
- Data-driven decision making

#### Q: What happens to my survey responses?
**A:** 
- Responses are confidential
- Used for analytics and reporting
- Shared with employers (anonymized)
- You can request deletion

#### Q: How long do I have to complete a survey?
**A:** 
- Typical timeframe: 5-7 days
- Reminders sent at: 3 days, 1 day before deadline
- Can request extension

#### Q: Who sees my feedback?
**A:** 
- Student: Can see their own feedback
- Employer: Sees only what's shared
- Admin: Sees aggregated data for analytics
- Never shared publicly

---

### Learning Modules

#### Q: How many modules should I complete?
**A:** 
- Minimum: 2 modules for certification
- Recommended: 5-8 modules
- Path varies by career sector
- Instructor guidance available

#### Q: Can I pause a module?
**A:** Yes, your progress is automatically saved:
- Close anytime without losing data
- Resume from where you left off
- No time limit (except deadline)

#### Q: What if I fail a quiz?
**A:** 
- You can retake unlimited times
- Each attempt helps you learn
- Best score is recorded
- Instructor feedback available

#### Q: How are my skills assessed?
**A:** Through:
- Quiz scores (40%)
- Project completion (30%)
- Instructor feedback (20%)
- Peer reviews (10%)

#### Q: Can I get a certificate?
**A:** Yes:
- After completing all modules (3+ recommended)
- Passing quiz requirements
- Positive employer feedback
- Certificate valid for 3 years

---

### Gamification & Rewards

#### Q: How do badges work?
**A:** 
- Earned by completing milestones
- Examples: "First Module", "Week Warrior", "Quiz Master"
- Visible on profile
- Shared in resumes/LinkedIn

#### Q: What are points for?
**A:** 
- Measure learning progress
- Unlock achievements
- Earn badges
- Track engagement
- 1 point per activity minute

#### Q: Can I lose points/badges?
**A:** 
- Points: No, only accumulate
- Badges: No, permanent once earned
- Points reset: Never (unless account deleted)

#### Q: What's the leaderboard based on?
**A:** 
- Points earned
- Modules completed
- Badges earned
- Quiz scores
- Updated weekly

---

### Troubleshooting

#### Problem: Can't log in

**Solution:**
1. Check email/password spelling
2. Reset password if forgotten
3. Clear browser cache
4. Try different browser
5. Contact support

**Cause:** Usually incorrect credentials or cache issue

---

#### Problem: Module won't load

**Solution:**
1. Refresh page (Ctrl+F5 or Cmd+Shift+R)
2. Check internet connection
3. Clear browser cache
4. Try incognito/private mode
5. Restart browser

**Cause:** Usually temporary connection issue

---

#### Problem: Can't submit survey

**Solution:**
1. Fill all required fields (marked with *)
2. Check data format (dates, numbers)
3. Try different browser
4. Clear cache and cookies
5. Save as draft first

**Cause:** Validation error or browser issue

---

#### Problem: Database connection error

**Solution:**
```bash
# Check if database file exists
ls -la mb/data/mb_app.db

# Reinitialize if needed
python scripts/init_db.py

# Check permissions
chmod 644 mb/data/mb_app.db
```

**Cause:** Database file missing or corrupted

---

#### Problem: Databricks connection timeout

**Solution:**
```bash
# Verify credentials in config/secrets.py
# Test connection
python -c "from app.integrations.databricks_connector import DatabricksConnector; dc = DatabricksConnector(); print(dc.test_connection())"

# Check firewall/VPN
# Verify workspace URL format
```

**Cause:** Network issue or wrong credentials

---

#### Problem: Azure Storage errors

**Solution:**
1. Verify storage account name
2. Check account key (not connection string)
3. Ensure container exists
4. Check blob permissions
5. Test with Azure Storage Explorer

**Cause:** Wrong credentials or insufficient permissions

---

#### Problem: Streamlit slow/unresponsive

**Solution:**
```bash
# Increase Python memory
python -Xmx512M -m streamlit run app/app.py

# Disable cache
streamlit run app/app.py --client.caching=false

# Use client-side caching
@st.cache_data(ttl=3600)
```

**Cause:** Usually memory issue or cache pollution

---

### Performance & Optimization

#### Q: Why is the app slow?
**A:** Possible causes:
1. **Database**: Too many queries
   - Solution: Use caching, optimize queries
2. **Network**: Slow internet
   - Solution: Check connection, retry
3. **Server**: High load
   - Solution: Scale up, use CDN
4. **Browser**: Too many tabs
   - Solution: Close other tabs, restart browser

#### Q: How can I improve performance?
**A:**
```python
# Use caching
@st.cache_data(ttl=3600)
def load_heavy_data():
    return expensive_operation()

# Lazy load components
if st.checkbox("Show advanced options"):
    advanced_section()

# Optimize queries
SELECT * FROM table WHERE date > CURRENT_DATE - 7  # Limit data
```

---

### Account Management

#### Q: How do I change my password?
**A:**
1. Login
2. Click profile → Settings
3. Click "Change Password"
4. Enter old password
5. Enter new password (twice)
6. Click "Save"

#### Q: How do I update my profile?
**A:**
1. Click profile menu
2. Select "Edit Profile"
3. Update desired fields
4. Click "Save Changes"
5. Verify email if changed

#### Q: Can I delete my account?
**A:**
1. Click settings
2. Scroll to "Danger Zone"
3. Click "Delete Account"
4. Confirm deletion
5. Data deleted after 90 days

#### Q: What if I forgot my password?
**A:**
1. Click "Forgot Password"
2. Enter email address
3. Check email for reset link
4. Click link (valid 1 hour)
5. Create new password

---

### Contact & Support

#### Q: How do I contact support?
**A:**
- **Email**: support@magicbus.org
- **Chat**: In-app support (9 AM - 5 PM IST)
- **Phone**: +91-XXX-XXX-XXXX
- **Response time**: Usually 24 hours

#### Q: How do I report a bug?
**A:**
1. Go to Help → Report Bug
2. Describe the issue
3. Include steps to reproduce
4. Attach screenshots if helpful
5. Submit (ticket ID provided)

#### Q: How do I request a feature?
**A:**
1. Go to Help → Feature Request
2. Describe the feature
3. Explain use case
4. Vote on existing requests
5. Submit

#### Q: Is there documentation?
**A:** Yes:
- **Wiki**: Full technical documentation
- **Quick Reference**: Common tasks
- **Video Tutorials**: Step-by-step guides
- **API Docs**: Developer reference

---

### Best Practices

#### For Students

1. **Consistency**: Study at same time daily
2. **Focus**: Minimize distractions during sessions
3. **Review**: Revisit completed modules weekly
4. **Feedback**: Actively seek peer feedback
5. **Goals**: Set clear learning objectives

#### For Instructors

1. **Content**: Update modules quarterly
2. **Feedback**: Respond within 24 hours
3. **Engagement**: Use gamification features
4. **Monitoring**: Track student progress weekly
5. **Communication**: Send weekly updates

#### For Admins

1. **Backups**: Daily database backups
2. **Monitoring**: Check health metrics daily
3. **Security**: Review access logs weekly
4. **Updates**: Apply patches promptly
5. **Planning**: Monthly capacity review

---

### Security Tips

1. **Password**: Use strong, unique passwords
2. **Sharing**: Never share your credentials
3. **Updates**: Keep browser/OS updated
4. **Wi-Fi**: Use VPN on public networks
5. **Phishing**: Report suspicious emails
6. **2FA**: Enable two-factor authentication (when available)

---

## Getting Help

### Help Resources

```
📚 Documentation    → docs/ folder
📖 Wiki             → docs/wiki/
🎥 Tutorials        → videos.magicbus.org
💬 Community Forum  → forum.magicbus.org
🐛 Bug Tracker      → github.com/magicbus/mb/issues
📧 Email Support    → support@magicbus.org
```

### Response Time SLA

| Issue Level | Priority | Response Time | Resolution Time |
|------------|----------|---------------|-----------------|
| Critical | P1 | 1 hour | 4 hours |
| High | P2 | 4 hours | 24 hours |
| Medium | P3 | 24 hours | 72 hours |
| Low | P4 | 48 hours | 1 week |

---

**Last Updated**: January 29, 2026
**Version**: 2.0
**Maintained By**: Support Team
