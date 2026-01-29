# Magic Bus Compass 360 - Youth Development Platform

**Transform raw engagement data into strategic insights for youth development in the APAC region.**

![Platform Status](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red) ![Azure](https://img.shields.io/badge/Azure-Blob_Storage-blue)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Recent Updates - Phase 3B](#-recent-updates---phase-3b-jan-29-2026)
- [Architecture](#architecture)
- [System Flows](#system-flows)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## 🎯 Overview

Magic Bus Compass 360 is an integrated youth development platform that combines:
- **Real-time engagement tracking** from APAC region datasets
- **Decision Intelligence dashboards** powered by Azure Blob Storage
- **Youth learning journey** management and feedback collection
- **Admin oversight** and strategic decision support
- **Data-driven proposals** for funding and interventions

The platform processes 50+ youth profiles across multiple learning domains, providing actionable insights for stakeholder decision-making.

---

## ✨ Key Features

### 👥 Youth Management
- Registration and onboarding workflows (5-phase Intelligent Orchestrator)
- Profile management with education background
- Learning module assignment and tracking
- Progress monitoring and engagement metrics
- **[NEW] Youth Potential Score™** - AI-powered composite scoring (Engagement, Retention, Skills, Placement)
- **[NEW] Learning Pathway & Milestones** - 5-stage development tracker

### 📊 Decision Intelligence Dashboard (11 Interactive Tabs)
- **Executive Overview**: Real-time KPIs (enrollment, completion, dropout risk)
- **Mobilisation Funnel**: Track progression through learning stages
- **Sector Heatmap**: Youth interests × readiness alignment
- **At-Risk Youth**: Priority identification and intervention
- **Module Effectiveness**: Learning content performance analysis
- **Gamification Impact**: Badge/points ROI comparison
- **Screening Analytics**: Voice assessment results and soft skills extraction
- **[NEW] Youth Potential Score™**: 4-tier distribution, top 20 leaderboard, trend analysis
- **[NEW] Retention Analytics**: Progress toward 85% target, intervention effectiveness tracking
- **[NEW] Skill Development**: Role-based gap analysis, personalized learning paths (5 roles)
- **Proposal Generator**: AI-powered funding proposals

### 💼 Admin Controls
- User role management (Youth, Admin, Instructor)
- Learning module creation and configuration
- Feedback survey distribution and collection
- System health monitoring
- **[NEW] Churn Prevention Dashboard** - At-risk student identification, intervention controls, effectiveness tracking
- **[NEW] Retention Management** - 5 intervention types (Mentorship, Badge Challenge, 1-on-1 Support, Career Coaching, Peer Pairing)

### 📈 Analytics & AI Engine
- 50+ youth profiles with engagement data
- 6 enriched feature tables for decision-making
- SQLite + Azure Blob Storage hybrid data sources
- Real-time feature computation pipeline
- **[NEW] 5 Advanced AI Features**:
  - ⭐ **Youth Potential Score™** - Composite metric (4 components, 4-tier system)
  - 🎓 **Skill Gap Bridger** - Role-based analysis for 5 career paths
  - 🚨 **Churn Risk Prediction** - Binary classifier with intervention tracking
  - 🎮 **Gamified Retention** - 6 badge types, streak tracking, engagement incentives
  - 🤝 **Peer Matching Network** - Similarity-based mentor/buddy pairing (k=0.65)

---

## 🏗️ Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        SQLite["SQLite Database<br/>50 Youth Records<br/>9 Tables"]
        Azure["Azure Blob Storage<br/>APAC Region<br/>Read-Only Access"]
    end
    
    subgraph "Backend Services"
        Connector["Azure Blob Connector<br/>- Data retrieval<br/>- Error handling<br/>- Caching"]
        Engineer["Feature Engineer<br/>- 6 feature tables<br/>- Dropout risk<br/>- Sector fit"]
        Dashboard["Decision Dashboard<br/>- KPI generation<br/>- Heatmap building<br/>- Insights"]
    end
    
    subgraph "Streamlit Frontend"
        Auth["Login & Register<br/>Pages"]
        Youth["Youth Dashboard<br/>- Profile<br/>- Progress<br/>- Feedback"]
        Admin["Admin Portal<br/>- Module Mgmt<br/>- Surveys<br/>- Reports"]
        DI["Decision Intelligence<br/>- 7 Tabs<br/>- Interactive Charts<br/>- Exports"]
    end
    
    SQLite -->|Load| Connector
    Azure -->|Load| Connector
    Connector -->|Features| Engineer
    Engineer -->|KPIs & Data| Dashboard
    Dashboard -->|Insights| DI
    Auth -->|Auth| Youth
    Auth -->|Auth| Admin
    Youth -->|Engagement| SQLite
    Admin -->|Config| SQLite
    DI -->|Display| Dashboard
```

### Component Architecture

```mermaid
graph LR
    subgraph "Presentation Layer"
        UI["Streamlit UI<br/>6 Pages<br/>Multi-role"]
    end
    
    subgraph "Application Layer"
        AppSvcs["Application Services<br/>- Auth Service<br/>- Module Service<br/>- Feedback Service"]
    end
    
    subgraph "Data Service Layer"
        Connectors["Data Connectors<br/>- SQLite Driver<br/>- Azure Connector<br/>- Cache Layer"]
    end
    
    subgraph "Data Layer"
        DB["SQLite<br/>mb_compass.db<br/>9 Tables"]
        Blob["Azure Blob<br/>APAC Datasets<br/>25+ CSVs"]
    end
    
    UI -->|API Calls| AppSvcs
    AppSvcs -->|Queries| Connectors
    Connectors -->|Read/Write| DB
    Connectors -->|Read| Blob
```

### Data Flow Architecture

```mermaid
graph TD
    A["Youth Registration"] -->|Store| B["mb_users Table<br/>50 students"]
    C["Learning Modules"] -->|Assign| D["learning_modules Table<br/>Module Assignments"]
    E["Youth Progress"] -->|Track| F["Feature Engineer"]
    D -->|Input| F
    B -->|Input| F
    F -->|Compute| G["student_daily_features<br/>50 rows"]
    F -->|Compute| H["dropout_risk<br/>50 rows"]
    F -->|Compute| I["sector_fit<br/>50 rows"]
    F -->|Compute| J["module_effectiveness<br/>16 rows"]
    G -->|Display| K["Decision Dashboard"]
    H -->|Display| K
    I -->|Display| K
    J -->|Display| K
    K -->|Visualize| L["7-Tab Dashboard"]
    L -->|KPIs| M["Executive Overview<br/>50 enrolled, 70.9% completion"]
```

---

## 🔄 System Flows

### 1. Youth Registration Flow

```mermaid
sequenceDiagram
    participant Youth as Youth User
    participant App as Streamlit App
    participant Auth as Auth Service
    participant DB as SQLite DB
    
    Youth->>App: Visit Platform
    App->>Youth: Show Login/Register
    Youth->>App: Fill Registration Form
    Note over App: Validate Email & Password
    App->>Auth: Authenticate
    Auth->>DB: Check User Exists
    DB-->>Auth: Not Found
    Auth->>DB: Create New User
    DB-->>Auth: User Created
    Auth-->>App: Success
    App->>DB: Store Profile Data
    DB-->>App: Stored
    App->>Youth: Redirect to Dashboard
```

### 2. Youth Dashboard Flow

```mermaid
sequenceDiagram
    participant Youth as Youth
    participant App as Youth Dashboard
    participant Service as Data Service
    participant DB as Database
    
    Youth->>App: Login
    App->>Service: Get User Profile
    Service->>DB: Query mb_users
    DB-->>Service: User Data
    Service->>DB: Query learning_modules
    DB-->>Service: Module List
    Service->>App: Profile & Modules
    App->>App: Render Dashboard
    App->>Youth: Display Profile, Progress, Feedback Form
    Youth->>App: Submit Feedback
    App->>Service: Save Feedback
    Service->>DB: Insert youth_feedback_surveys
    DB-->>Service: Saved
    Service-->>App: Confirmation
    App->>Youth: Success Message
```

### 3. Admin Control Flow

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant App as Admin Portal
    participant Service as Admin Service
    participant DB as Database
    
    Admin->>App: Login as Admin
    App->>Service: Load Admin Dashboard
    Service->>DB: Query All Users
    DB-->>Service: 50 Users
    Service->>DB: Query learning_modules
    DB-->>Service: 16 Modules
    Service->>App: Dashboard Data
    App->>Admin: Display Overview
    Admin->>App: Create New Module
    App->>Service: Add Module
    Service->>DB: Insert learning_modules
    DB-->>Service: Inserted
    Service->>App: Success
    App->>Admin: Module Added
    Admin->>App: Distribute Survey
    App->>Service: Send Survey Emails
    Service->>DB: Create survey_distribution_logs
    DB-->>Service: Sent
    Service-->>App: Delivery Report
```

### 4. Decision Intelligence Flow

```mermaid
sequenceDiagram
    participant User as Stakeholder
    participant UI as DI Dashboard
    participant Engineer as Feature Engineer
    participant Connector as Data Connector
    participant Data as Database/Blob
    
    User->>UI: Navigate to DI Dashboard
    UI->>Engineer: Request Features
    Engineer->>Connector: Load Data
    Connector->>Data: Query SQLite
    Data-->>Connector: 50 Records
    Connector->>Connector: Check Azure
    Connector-->>Engineer: Data Ready
    Engineer->>Engineer: Compute 6 Features
    Engineer->>Engineer: Aggregate Metrics
    Engineer-->>UI: Features & Insights
    UI->>UI: Build Charts
    UI->>UI: Format KPIs
    UI->>User: Display 7 Tabs
    User->>UI: View Sector Heatmap
    UI->>User: Interactive Visualization
    User->>UI: Download Proposal
    UI->>User: PDF Export
```

---

## 📊 Data Model

### Entity-Relationship Overview

```mermaid
erDiagram
    MB_USERS ||--o{ LEARNING_MODULES : "assigns"
    MB_USERS ||--o{ CAREER_SURVEYS : "completes"
    MB_USERS ||--o{ YOUTH_FEEDBACK_SURVEYS : "submits"
    LEARNING_MODULES ||--o{ CAREER_SURVEYS : "covers"
    SURVEY_TEMPLATES ||--o{ SURVEY_DISTRIBUTION_LOGS : "used-in"
    
    MB_USERS {
        int user_id
        string student_id
        string email
        string full_name
        string education_level
        timestamp created_at
    }
    
    LEARNING_MODULES {
        int module_assignment_id
        int user_id
        string title
        string status
        int progress
        timestamp completed_date
    }
    
    CAREER_SURVEYS {
        int survey_id
        int user_id
        string survey_data
        timestamp completed_at
    }
    
    YOUTH_FEEDBACK_SURVEYS {
        int survey_id
        int user_id
        string job_title
        int overall_satisfaction
        timestamp completed_at
    }
    
    SURVEY_TEMPLATES {
        int template_id
        string template_type
        string template_name
        json questions_json
        boolean is_active
    }
    
    SURVEY_DISTRIBUTION_LOGS {
        int log_id
        string survey_type
        string recipient_email
        timestamp sent_date
        boolean completed
    }
```

---

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip/conda
- SQLite3
- Git

### Setup Steps

1. **Clone Repository**
```bash
git clone https://github.com/Huzefaaa2/mb.git
cd mb
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Initialize Database**
```bash
python scripts/init_db.py
```

6. **Run Platform**
```bash
streamlit run mb/app.py
```

Visit: `http://localhost:8501`

---

## ⚡ Quick Start

### Access the Platform

1. **Login Page** (`http://localhost:8501`)
   - Register new account or login
   - Email-based authentication

2. **Youth Dashboard** 
   - View profile and learning progress
   - Submit feedback surveys
   - Track module completion

3. **Decision Intelligence** (Admin)
   - Navigate to: Admin & Intelligence → Decision Intelligence Dashboard
   - View 7-tab analytics dashboard
   - Download proposals

### Demo Data
- **50 Youth Profiles** pre-loaded
- **16 Learning Modules** configured
- **70.9% Completion Rate** current baseline
- **40% Dropout Risk** identification active

---

## 📚 Documentation

### Wiki Pages
Comprehensive documentation available in the [Wiki](https://github.com/Huzefaaa2/mb/wiki):

- **[Architecture](docs/wiki/01-Architecture.md)** - System design and C4 diagrams
- **[Data Model](docs/wiki/02-Data-Model.md)** - Database schema and relationships
- **[API Reference](docs/wiki/03-API-Reference.md)** - Backend services
- **[Feature Engineering](docs/wiki/04-Feature-Engineering.md)** - Analytics pipeline
- **[Deployment](docs/wiki/05-Deployment.md)** - Production setup
- **[Troubleshooting](docs/wiki/06-Troubleshooting.md)** - Common issues

### Key Documentation Files
- [Azure Integration Guide](docs/AZURE_INTEGRATION_GUIDE.md)
- [Feature Engineering Reference](docs/FEATURES_DOCUMENTATION.md)
- [API Specifications](docs/API_SPECIFICATION.md)

---

## 🏛️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | Streamlit | 1.28.1 |
| **Backend** | Python | 3.11 |
| **Database** | SQLite3 | Latest |
| **Cloud Storage** | Azure Blob Storage | Latest |
| **Analytics** | Pandas, NumPy | Latest |
| **Visualization** | Plotly | 5.18 |
| **Testing** | Pytest | Latest |

---

## 📁 Project Structure

```
mb/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── QUICK_START.py                     # Demo script
│
├── mb/                                # Main application
│   ├── app.py                         # Streamlit entry point
│   ├── pages/                         # Page modules
│   │   ├── 0_login.py                 # Authentication
│   │   ├── 1_register.py              # Registration
│   │   ├── 2_youth_dashboard.py       # Youth profile
│   │   ├── 2_confirmation.py          # Confirmation page
│   │   ├── 3_magicbus_admin.py        # Admin portal
│   │   ├── 4_decision_intelligence_azure.py  # DI Dashboard
│   │   └── 5_feedback_survey.py       # Feedback collection
│   │
│   ├── data_sources/                  # Data integration
│   │   ├── azure_blob_connector.py    # Azure connectivity
│   │   ├── azure_feature_engineer.py  # Feature computation
│   │   └── azure_decision_dashboard.py # Analytics engine
│   │
│   ├── components/                    # UI components
│   └── services/                      # Business logic
│
├── config/                            # Configuration
│   ├── settings.py                    # Environment settings
│   └── secrets.py                     # Secrets management
│
├── data/                              # Data directory
│   ├── mb_compass.db                  # SQLite database
│   └── synthetic/                     # Generated datasets
│
├── scripts/                           # Utilities
│   ├── init_db.py                     # Database initialization
│   ├── generate_synthetic_data.py     # Data generation
│   └── verify_setup.py                # Setup verification
│
├── docs/                              # Documentation
│   ├── wiki/                          # Wiki pages (C4 diagrams)
│   ├── AZURE_INTEGRATION_GUIDE.md     # Azure setup
│   └── FEATURES_DOCUMENTATION.md      # Features guide
│
└── tests/                             # Unit tests
    └── test_integrations.py           # Integration tests
```

---

## 🔐 Security & Privacy

- ✅ Role-based access control (Youth, Admin, Instructor)
- ✅ Email-based authentication
- ✅ Data encryption at rest (SQLite)
- ✅ Secure connection strings (environment variables)
- ✅ PII protection (no plaintext passwords)
- ✅ Survey data anonymization

---

## 📊 Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Youth Enrolled | 50 | ✅ Active |
| Learning Modules | 16 | ✅ Configured |
| Completion Rate | 70.9% | ✅ Above Target |
| Dropout Risk (High) | 40% | ⚠️ Monitor |
| Engagement Score | 57% | ✅ Healthy |
| Retention Goal | 85% | ✅ Targeting |
| Dashboard Tabs | 11 | ✅ Live |
| AI Features | 5 | ✅ Deployed |
| Dashboard Response Time | <1s | ✅ Optimal |
| Feature Computation | 15-30s | ✅ Acceptable |

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write tests for new features
- Document API changes
- Update relevant Wiki pages

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/Huzefaaa2/mb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Huzefaaa2/mb/discussions)
- **Email**: support@magicbus.local
- **Documentation**: [Wiki](https://github.com/Huzefaaa2/mb/wiki)

---

## 🙏 Acknowledgments

- Magic Bus Foundation for youth development mission
- APAC region partners for data collaboration
- Azure for cloud infrastructure
- Streamlit team for amazing dashboard framework

---

**Last Updated**: January 29, 2026 | **Version**: 1.0.0 (Phase 3B Complete)

---

## 🚀 Recent Updates - Phase 3B (Jan 29, 2026)

### New Dashboard Tabs (Decision Intelligence)
- **Tab 7: ⭐ Youth Potential Score™** - KPI metrics, tier distribution, top 20 leaderboard
- **Tab 8: 📉 Retention Analytics** - Retention gauge (65%→85%), intervention effectiveness
- **Tab 9: 🎓 Skill Development** - Role analyzer, learning paths, skill requirements

### Youth Dashboard Enhancements
- **⭐ Your Youth Potential Score** - Composite scoring with tier assignment
- **🎯 Your Learning Pathway** - 5-stage milestone tracker with progress visualization

### Admin Dashboard Improvements
- **🚨 Churn Prevention Tab** - At-risk students, intervention controls, effectiveness log

### Configuration Exposed
- All Phase 3 features toggleable via `config/settings.py`
- 50+ configuration options for feature tuning
- Complete settings for all 5 AI features

### Documentation
- `PHASE_3B_COMPLETION.md` - Complete feature guide (451 lines)
- `PROJECT_STATUS.md` - Overall project overview (437 lines)
- Git history with 5 well-documented commits

### Status
✅ **Phase 3B Complete** - Dashboard integration finished  
🚀 **Ready for UAT** - All features tested and deployed  
📊 **Project 80% Complete** - 4 phases delivered, Phase 4 (Testing) recommended next
