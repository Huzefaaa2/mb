# Azure Decision Intelligence Dashboard - Quick Start

## 🚀 5-Minute Setup

### Step 1: Launch the Dashboard
```bash
cd c:\Users\HHusain\mb
streamlit run mb/app.py
```

### Step 2: Navigate to Dashboard
- Go to **Admin & Intelligence** in left sidebar
- Click **🧠 Decision Intelligence**
- You'll see the new Azure-powered dashboard

### Step 3: Test Azure Connection
- Look for **📊 Data Source** section in sidebar
- Click **🔗 Test Connection**
- See "✅ Connected to Azure" message
- Display shows number of available datasets

### Step 4: Compute Features
- In sidebar, click **🔄 Compute Features**
- Wait 15-30 seconds for completion
- See checkmarks for each computed feature:
  - ✅ student_daily_features
  - ✅ dropout_risk
  - ✅ sector_fit
  - ✅ module_effectiveness
  - ✅ gamification_impact
  - ✅ mobilisation_funnel

### Step 5: Explore Dashboard Tabs

#### 📊 Tab 1: Executive Overview
**What you see:** 7 KPI cards showing:
- 👥 Youth Enrolled
- 🎯 Active Learners  
- 📚 Completion Rate
- ⚠️ Dropout Risk
- 📋 Quiz Score
- ✅ Quiz Pass Rate
- 💪 Engagement Score

**Use it for:** Quick health check of program

#### 📈 Tab 2: Mobilisation Funnel
**What you see:** Funnel chart showing progression stages

**What it tells you:**
- How many students progress from Registered → Learning → Quiz → Achievement
- Where students drop off most

**Take action:** Click on stages to identify bottlenecks

#### 🔥 Tab 3: Sector Heatmap
**What you see:** Color-coded grid of sectors vs readiness

**Colors mean:**
- 🟢 Green = High readiness (Ready for job)
- 🟡 Amber = Medium readiness (Developing skills)
- 🔴 Red = Low readiness (Needs support)

**Take action:** Focus on Red sectors for training

#### 🚨 Tab 4: At-Risk Youth
**What you see:** List of students needing help

**Filters available:**
- Risk Level: HIGH, MEDIUM, LOW, or ALL
- Top N students (10-100)

**Each row shows:**
- Student name & email
- Risk level & score (1-9)
- Reason for risk (e.g., "Low module engagement")

**Take action:** Contact HIGH risk students for interventions

#### 📚 Tab 5: Module Effectiveness
**What you see:** Bar chart of module completion rates

**Effectiveness levels:**
- 🟢 High Impact (≥80% completion) → Scale up
- 🟡 Medium Impact (60-79%) → Monitor
- 🔴 Needs Improvement (<60%) → Revise

**Take action:** 
- Promote high-impact modules
- Review or redesign low-performing modules

#### 🏅 Tab 6: Gamification Impact
**What you see:** Comparison of badge earners vs non-badge users

**Key metrics:**
- User count in each group
- Completion rate comparison
- Engagement score difference

**Example insight:**
- Badge earners: 75% completion
- Non-badge: 52% completion
- **Impact: +23% lift from gamification**

**Take action:** Invest in gamification if ROI is positive

#### 💡 Tab 7: Proposal Generator
**What to do:**
1. (Optional) Enter sector name (e.g., "IT", "Healthcare")
2. (Optional) Enter grade level
3. Click **📄 Generate Proposal**
4. Review auto-generated proposal with:
   - Executive summary
   - Key metrics & impact highlights
   - At-risk analysis
   - Module recommendations
   - Funding requirements
   - ROI projection

**Use for:** Present to board, donors, government

---

## 📊 Understanding the Data

### Where does data come from?

**Azure Blob Storage** with these 25+ tables:

**Student Data:**
- students → enrollment info
- student_progress → what modules they completed
- student_skills → assessed skill levels

**Learning Data:**
- learning_modules → course definitions
- lessons → individual lessons
- quizzes → assessment questions
- quiz_attempts → student answers

**Career Data:**
- career_interests → sectors students like
- career_pathways → job path info
- skills → skill definitions

**Engagement Data:**
- daily_challenges → tasks given to students
- achievements → badges earned
- points_ledger → gamification points
- user_sessions → login activity

---

## 🎯 Common Tasks

### "I need to find students most likely to drop out"
1. Go to Tab 4: **🚨 At-Risk Youth**
2. Filter by "HIGH" risk level
3. Sort by Risk Score (descending)
4. Contact top 20 students
5. Implement interventions:
   - SMS reminders
   - Peer mentoring
   - Extra practice modules
   - Motivational calls

### "Which modules are working best?"
1. Go to Tab 5: **📚 Module Effectiveness**
2. Look for green bars (High Impact)
3. Check completion rates
4. **Action:** Scale these modules to more students

### "Do badges help students learn?"
1. Go to Tab 6: **🏅 Gamification Impact**
2. Compare completion rates:
   - Badge earners: X%
   - Non-badge: Y%
3. If difference > 10%, gamification is working
4. **Action:** Expand gamification program

### "I need to pitch to donors"
1. Go to Tab 7: **💡 Proposal Generator**
2. Click **📄 Generate Proposal**
3. Review auto-generated content:
   - Real numbers from data
   - Impact metrics
   - Funding needs
4. Download as text
5. **Copy-paste into deck or doc**

### "Attendance is low - where's the problem?"
1. Go to Tab 2: **📈 Mobilisation Funnel**
2. Identify where most students drop off
3. **Example:** If most drop between "Registered" and "Started Learning":
   - Problem: Low engagement from start
   - Fix: Onboarding improvements
4. If drop between "Learning" and "Quiz":
   - Problem: Content too hard
   - Fix: Simplify or add support

---

## 🔄 When to Refresh

**Refresh features when:**
- You add new students
- Month ends (to update progress)
- Before generating proposal for board
- After running major intervention

**How to refresh:**
1. Sidebar → Click **🔄 Compute Features**
2. Wait 15-30 seconds
3. See "✅ Features computed!" 
4. Refresh browser (F5)
5. New data appears in all tabs

---

## 📱 What Each Metric Means

| Metric | What It Is | Target | Action If Low |
|--------|-----------|--------|----------------|
| Youth Enrolled | Total students | Growing | Recruitment drive |
| Active Learners | % with progress | >80% | Engagement boost |
| Completion Rate | % modules finished | >75% | Content review |
| Dropout Risk | % at-risk | <10% | Targeted support |
| Quiz Pass Rate | % quizzes passed | >70% | Difficulty check |
| Module Effectiveness | Completion % | >80% | Module revision |
| Engagement Score | Composite score | >75% | Holistic review |

---

## ⚠️ Key Insights to Look For

### 🚨 Red Flags
- Dropout risk > 20% → Intervention needed
- Funnel drops >50% between stages → Process problem
- Module completion <50% → Content issue
- Sector heatmap all red → Skills gap

### 🟢 Green Flags
- Dropout risk <10% → Program working
- Funnel steady across stages → Good engagement
- Module completion >80% → Effective content
- Gamification lift >15% → ROI positive

### 🟡 Action Items
- Amber sectors → Priority training
- MEDIUM risk students → Mentoring
- Needs Improvement modules → Quick revamp
- Underutilized features → Marketing needed

---

## 🤖 Azure Data Features

### Real-Time Data
All metrics update from live Azure datasets:
- When you click **🔄 Compute Features**
- Dashboard recalculates from latest data
- No manual updates needed

### Automatic Calculations
System computes (you don't need to):
- Dropout risk scores (1-9 scale)
- Sector fit (0-100 scale)
- Module effectiveness levels
- Gamification impact %
- Funnel progression %

### Smart Filtering
- At-risk youth: Filter by risk level
- Module effectiveness: Sort by metric
- Proposal generator: Filter by sector
- Heatmap: View all sectors at once

---

## 📥 Exporting Data

### Export Proposal
1. Generate proposal (Tab 7)
2. Click **📥 Download Proposal as Text**
3. Opens text file with full proposal
4. Use in Word doc or presentation

### Export Dashboard Tab Data
- Each tab has dataframe display
- Click the download icon (⬇️) in top-right
- Saves as CSV file
- Open in Excel for analysis

### Manual Export for Analysis
```python
# In Python terminal:
from azure_decision_dashboard import get_azure_dashboard
dashboard = get_azure_dashboard()

# Get any metric
at_risk = dashboard.get_at_risk_youth(limit=100)
at_risk.to_csv("at_risk_students.csv")

effectiveness = dashboard.get_module_effectiveness()
effectiveness.to_csv("module_effectiveness.csv")
```

---

## 🆘 Troubleshooting

### Dashboard shows "No data available"
✅ **Fix:** Click **🔄 Compute Features** in sidebar

### "Connection failed" error
✅ **Fix:** 
- Check internet connection
- Click **🔗 Test Connection** 
- If still fails, wait 30 seconds and retry

### Funnel/Heatmap chart is blank
✅ **Fix:**
- Refresh browser (F5)
- Compute features again
- Check that datasets have data

### At-risk list is empty
✅ **Fix:**
- Program might be very healthy (low dropout!)
- Adjust risk thresholds if needed
- Check feature computation completed

---

## 📞 Support

**For issues:**
1. Check Azure connection first (🔗 button)
2. Try computing features again (🔄 button)
3. Refresh browser (F5)
4. Restart dashboard app
5. Contact data team

---

## 📚 Learn More

- **Full Guide:** See `AZURE_INTEGRATION_GUIDE.md`
- **Feature Details:** See `DATABRICKS_SQL_REFERENCE.md`
- **Proposal Tips:** See `JUDGE_QA_CHEATSHEET.md`

---

**Ready to use?** Start with Step 1 above! ⬆️

**Last Updated:** January 29, 2026
