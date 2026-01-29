# 🚀 Decision Intelligence Dashboard - Quick Start (5 Min)

## What Is This?

Magic Bus Compass 360 now has a **Decision Intelligence Dashboard** that:
- 🔴 **Predicts** which students will drop out
- 🟢 **Recommends** which sectors fit best  
- 📊 **Ranks** which training modules work best
- 💡 **Generates** funding proposals from real data

---

## Getting Started (30 seconds)

### 1. Open the Dashboard
```
URL: http://localhost:8501
Sidebar: Admin & Intelligence → 🧠 Decision Intelligence
```

### 2. First Time Setup
```
Click: "🔄 Refresh All Features" (top sidebar)
Wait: ~15-20 seconds
See: "✅ All features refreshed!"
```

### 3. Start Exploring
Go to any of these tabs:
- **📊 Executive Overview** → See overall health
- **🚨 At-Risk Youth** → See students who need help NOW
- **💡 Proposal Generator** → Generate a funding proposal in 2 minutes

---

## 7 Tabs Explained

### Tab 1: 📊 Executive Overview
**What you see**: 4 big numbers
- 👥 Youth Enrolled (total students)
- 🎯 Active Learners (students currently engaged)  
- 📚 Completion Rate (% finished modules)
- ⚠️ Dropout Risk (% in danger)

**What to do**: If dropout risk is high (>20%), go to Tab 4 to help students.

---

### Tab 2: 📈 Mobilisation Funnel
**What you see**: A funnel showing student journey
```
Registered       ████ 100% (4,832 students)
Survey Done      ███  82% (3,961 students)
Learning Started ██   60% (2,871 students)
Completed        █    49% (2,369 students)
```

**What to do**: Look for big drops. If 20% drop between steps → investigate that step.

---

### Tab 3: 🔥 Sector Heatmap
**What you see**: A color grid showing:
- X-axis: Job sectors (IT, Hospitality, Retail, Healthcare)
- Y-axis: Readiness (Green = ready, Amber = needs help, Red = not ready)

**What to do**: 
- **Green sectors**: Recommend for placement
- **Amber sectors**: Need skill bridging first
- **Red sectors**: Student chose wrong path, offer pivot

---

### Tab 4: 🚨 At-Risk Youth Intervention Board
**What you see**: A list of students in danger, sorted by urgency

| Student ID | Reason | Risk | Action |
|-----------|--------|------|--------|
| S1023 | No modules started | HIGH | 🎯 Call today |
| S1142 | Low quiz scores | MEDIUM | 📞 Check-in 48h |
| S2091 | No activity 7 days | HIGH | ⚠️ Escalate |

**What to do**:
1. Click on a student
2. See their risk reason
3. Assign a teacher mentor
4. Send micro-learning module
5. Check-in 48h later

---

### Tab 5: 📚 Module Effectiveness & ROI
**What you see**: A bar chart + table of modules ranked by completion rate

| Module | Learners | Completion | Impact |
|--------|----------|-----------|--------|
| Customer Comm | 245 | 82% | ⭐⭐⭐ High |
| Excel Basics | 312 | 76% | ⭐⭐ Medium |
| Interview Prep | 198 | 88% | ⭐⭐⭐ High |
| Tech Skills | 89 | 45% | ❌ Needs Redesign |

**What to do**:
- **High Impact (≥80%)**: Scale to all students
- **Medium (60-79%)**: Pair with mentoring
- **Low (<60%)**: Redesign or remove

---

### Tab 6: 🏅 Gamification Impact
**What you see**: Are badges/streaks working?

```
Badge Earners:      82% completion ✅
Non-Badge Earners:  54% completion ⚠️

Difference: +28 percentage points!
```

**What to do**: If badge earners complete more → scale gamification features!

---

### Tab 7: 💡 Proposal Generator (The Secret Weapon)
**What you see**: A form with 2 dropdowns

```
Region: [Select]  ▾
Sector: [Select]  ▾

[🚀 Generate Proposal Insights]
```

**What to do**:
1. Pick a region (AP, TG, KA, MH, All India)
2. Pick a sector (IT, Hospitality, Retail, etc.)
3. Click "Generate"
4. Wait 5 seconds
5. Copy-paste the proposal
6. Customize for your donor
7. Send it!

**Example Output**:
```
"Magic Bus trained 4,200 youth in AP.
Using AI sector-fit discovery, we reduced dropouts by 22%.
Investment of ₹X will enable 10,000 youth placement model.
Expected outcomes: 3,200 placements, ₹Y revenue."
```

---

## Daily Workflow (Charity Staff)

### Morning (5 min)
1. Open Decision Intelligence dashboard
2. Go to **At-Risk Youth** tab
3. See today's priority list
4. Assign teachers to HIGH risk students

### Weekly (1 hour)
1. Review **Sector Heatmap** 
2. Adjust curriculum if sectors have low readiness
3. Click "🔄 Refresh All Features" to get latest data

### Monthly (2 hours)
1. Export **Executive Overview** metrics
2. Update board presentation with KPIs
3. Review **Module Effectiveness** 
4. Plan which modules to scale/redesign

### When Raising Funds (1 hour)
1. Go to **Proposal Generator**
2. Select target region + sector
3. Generate proposal
4. Customize + send to CSR partner

---

## Key Numbers to Remember

| Metric | Your Target | How to Achieve |
|--------|------------|----------------| 
| Dropout Rate | <25% | Use At-Risk Board to intervene |
| Completion Rate | >75% | Scale modules with >80% effectiveness |
| Sector Fit | >60% Green | Use sector survey on Day 1 |
| Intervention Success | >80% | Contact within 48h of at-risk flag |

---

## Troubleshooting

### Dashboard shows "No data"?
**Solution**: Click "🔄 Refresh All Features" in sidebar and wait 20 seconds

### Can't find the Decision Intelligence tab?
**Solution**: 
1. Check sidebar → Admin & Intelligence section
2. If not there, restart app: `streamlit run mb/app.py`

### Proposal Generator not working?
**Solution**: 
- It's normal if it takes 10 seconds (Azure OpenAI might be slow)
- If it fails, you'll still see a template-based proposal (works offline!)

### Numbers seem wrong?
**Solution**: 
1. Data refreshes weekly (every Monday 2 AM)
2. For fresh data, manually click "🔄 Refresh All Features"

---

## Pro Tips

### Tip 1: Export Everything
- Take screenshots of dashboards
- Download proposal as PDF
- Share with board/donors

### Tip 2: Set Weekly Alerts
- High dropout risk increasing? 🚨
- Low completion rate? ⚠️
- New at-risk students? 📢

### Tip 3: Track Impact Over Time
- Refresh features every Monday
- Compare Month 1 vs Month 2
- Show year-over-year improvements to donors

### Tip 4: Customize Proposals
- Auto-generated proposal is a starting point
- Add region-specific context
- Include donor's focus areas (jobs, skills, diversity)
- Add your Magic Bus brand/mission

---

## What's Behind The Magic?

**Databricks Feature Engineering** (Backend):
- 🔴 **Dropout Risk Table**: Predicts who needs help (HIGH/MEDIUM/LOW)
- 🟢 **Sector Fit Table**: Matches students to right jobs
- 📚 **Module Effectiveness Table**: Ranks training by ROI
- 📊 **Funnel Table**: Tracks progression through program
- 🏅 **Gamification Table**: Compares badge earners vs others

**All data is real** → pulled from your SQLite database → computed weekly → shown in dashboards

---

## Next Steps

### This Week
- [ ] Explore all 7 tabs
- [ ] Generate 1 proposal
- [ ] Send to a CSR partner
- [ ] Get feedback

### This Month
- [ ] Use At-Risk Board to help 10 students
- [ ] Identify 2-3 high-impact modules to scale
- [ ] Present dashboard to board

### This Quarter
- [ ] Automate feature refresh (weekly email of key metrics)
- [ ] Train staff on dashboard
- [ ] Generate 5+ funding proposals
- [ ] Raise ₹X using data-backed proposals

---

## Questions?

- **For Staff**: See `DECISION_INTELLIGENCE_GUIDE.md` → Troubleshooting section
- **For Judges**: See `JUDGE_QA_CHEATSHEET.md` → 10 hardest questions
- **For Technical**: See `DATABRICKS_SQL_REFERENCE.md` → Feature definitions

---

## 🎉 You're All Set!

The **Decision Intelligence Platform** is now live.  
Start predicting, recommending, and proving impact! 🚀

---

*Quick Start Guide | 5 minutes to impact | January 29, 2026*
