# Architecture Overview

## C4 Model - System Context Diagram

```mermaid
graph TB
    subgraph System
        MB["🧠 Magic Bus<br/>Compass 360"]
    end
    
    subgraph Users
        Youth["👥 Youth Users<br/>Learning & Feedback"]
        Admin["👨‍💼 Admin Users<br/>System Management"]
        Stakeholder["🎯 Stakeholders<br/>Decision Making"]
    end
    
    subgraph External
        Azure["☁️ Azure Blob Storage<br/>APAC Datasets"]
        Email["📧 Email Service<br/>Survey Distribution"]
    end
    
    Youth -->|Register, Learn, Feedback| MB
    Admin -->|Configure, Monitor| MB
    Stakeholder -->|View Insights| MB
    MB -->|Read Data| Azure
    MB -->|Send Surveys| Email
```

## C4 Model - Container Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Web["🌐 Web Application<br/>(Streamlit)<br/>- 6 Pages<br/>- Multi-role UI<br/>- Responsive"]
    end
    
    subgraph "Application Layer"
        Auth["🔐 Auth Module<br/>- User Management<br/>- Role Control<br/>- Session Mgmt"]
        Youth["👤 Youth Service<br/>- Profile Management<br/>- Progress Tracking<br/>- Feedback"]
        Admin["⚙️ Admin Service<br/>- Module Config<br/>- Survey Mgmt<br/>- System Health"]
        DI["📊 Decision Intelligence<br/>- Feature Compute<br/>- KPI Generation<br/>- Analytics"]
    end
    
    subgraph "Data Layer"
        DB["🗄️ SQLite Database<br/>- 9 Tables<br/>- 50 Users<br/>- 16 Modules"]
        Cache["💾 Cache Layer<br/>- Feature Cache<br/>- Dataset Cache<br/>- Session Cache"]
    end
    
    subgraph "External Services"
        Azure["☁️ Azure Blob<br/>- 25+ Datasets<br/>- APAC Region<br/>- Read-Only"]
    end
    
    Web -->|API Calls| Auth
    Web -->|API Calls| Youth
    Web -->|API Calls| Admin
    Web -->|API Calls| DI
    
    Auth -->|Query| DB
    Youth -->|Query/Update| DB
    Admin -->|Query/Update| DB
    DI -->|Query| DB
    DI -->|Cache| Cache
    
    DI -->|Read| Azure
    Auth -->|Store/Verify| Cache
```

## C4 Model - Component Diagram (Detail View)

```mermaid
graph TB
    subgraph "Frontend - Streamlit Pages"
        Login["Login Page<br/>- Email/Password<br/>- Register Link"]
        Register["Register Page<br/>- Form Validation<br/>- Profile Setup"]
        Youth["Youth Dashboard<br/>- Profile View<br/>- Progress Tracker<br/>- Feedback Form"]
        Admin["Admin Portal<br/>- User List<br/>- Module Manager<br/>- Survey Panel"]
        DI["DI Dashboard<br/>- 7 Tabs<br/>- Charts<br/>- Exports"]
        Confirm["Confirmation<br/>- Success Messages<br/>- Navigation"]
    end
    
    subgraph "Backend Services"
        AuthSvc["Auth Service<br/>- validate_credentials()<br/>- create_session()<br/>- get_user_role()"]
        YouthSvc["Youth Service<br/>- get_profile()<br/>- update_progress()<br/>- submit_feedback()"]
        AdminSvc["Admin Service<br/>- list_users()<br/>- create_module()<br/>- send_surveys()"]
        DISvc["DI Service<br/>- compute_features()<br/>- get_kpis()<br/>- build_heatmap()"]
    end
    
    subgraph "Data Access Layer"
        SQLite["SQLite Driver<br/>- execute_query()<br/>- insert_record()<br/>- update_record()"]
        AzureConn["Azure Connector<br/>- get_dataset()<br/>- list_blobs()<br/>- handle_errors()"]
        FeatureEng["Feature Engineer<br/>- compute_all_features()<br/>- load_from_sqlite()<br/>- aggregate_metrics()"]
    end
    
    Login -->|Login| AuthSvc
    Register -->|Register| AuthSvc
    Youth -->|Get Profile| YouthSvc
    Youth -->|Submit Feedback| YouthSvc
    Admin -->|List/Create| AdminSvc
    DI -->|Compute| DISvc
    
    AuthSvc -->|Query| SQLite
    YouthSvc -->|Query/Update| SQLite
    AdminSvc -->|Query/Update| SQLite
    DISvc -->|Query Features| FeatureEng
    
    FeatureEng -->|Load Data| SQLite
    FeatureEng -->|Read| AzureConn
    AzureConn -->|Connect| Azure["Azure Blob<br/>Storage"]
```

## C4 Model - Code Level (Detailed)

```mermaid
graph LR
    subgraph "mb/pages"
        Page0["0_login.py<br/>Entry point"]
        Page1["1_register.py<br/>Registration logic"]
        Page2Y["2_youth_dashboard.py<br/>Youth UI"]
        Page3["3_magicbus_admin.py<br/>Admin UI"]
        Page4["4_decision_intelligence_azure.py<br/>DI Dashboard"]
    end
    
    subgraph "mb/data_sources"
        Connector["azure_blob_connector.py<br/>AzureBlobConnector class<br/>- get_dataset()<br/>- list_available_datasets()<br/>- get_health_report()"]
        Engineer["azure_feature_engineer.py<br/>AzureFeatureEngineer class<br/>- compute_all_features()<br/>- compute_student_daily_features()<br/>- compute_dropout_risk()"]
        Dashboard["azure_decision_dashboard.py<br/>AzureDecisionDashboard class<br/>- get_executive_overview()<br/>- get_sector_heatmap()<br/>- generate_proposal_insights()"]
    end
    
    subgraph "config"
        Settings["settings.py<br/>Environment config"]
        Secrets["secrets.py<br/>Key management"]
    end
    
    Page4 -->|Uses| Dashboard
    Dashboard -->|Uses| Engineer
    Engineer -->|Uses| Connector
    Dashboard -->|Config| Settings
    Connector -->|Config| Settings
```

## Data Flow Architecture

### Request Flow - Youth Dashboard

```mermaid
sequenceDiagram
    participant Browser
    participant Streamlit
    participant YouthService
    participant SQLite
    participant Cache
    
    Browser->>Streamlit: Click Youth Dashboard
    Streamlit->>Streamlit: Check Session
    Streamlit->>YouthService: get_user_profile(user_id)
    YouthService->>Cache: Check Cache
    alt Cache Hit
        Cache-->>YouthService: Cached Profile
    else Cache Miss
        YouthService->>SQLite: SELECT from mb_users
        SQLite-->>YouthService: Profile Data
        YouthService->>Cache: Store in Cache
    end
    YouthService-->>Streamlit: Profile Object
    Streamlit->>Streamlit: Render UI
    Streamlit-->>Browser: Display Dashboard
```

### Request Flow - Decision Intelligence

```mermaid
sequenceDiagram
    participant Admin
    participant DI_Dashboard
    participant FeatureEngineer
    participant AzureConnector
    participant SQLite
    participant Azure
    
    Admin->>DI_Dashboard: Click "Refresh Features"
    DI_Dashboard->>FeatureEngineer: compute_all_features()
    FeatureEngineer->>AzureConnector: get_dataset("students")
    AzureConnector->>Azure: Request Data
    alt Azure Available
        Azure-->>AzureConnector: CSV Data
    else Azure Unavailable
        AzureConnector->>SQLite: Fallback Load
        SQLite-->>AzureConnector: SQLite Data
    end
    AzureConnector-->>FeatureEngineer: DataFrame
    FeatureEngineer->>FeatureEngineer: Compute 6 Features
    FeatureEngineer-->>DI_Dashboard: Features Dict
    DI_Dashboard->>DI_Dashboard: Generate KPIs
    DI_Dashboard-->>Admin: Display Dashboard
```

## Technology Stack Architecture

```mermaid
graph TB
    subgraph "Presentation"
        Streamlit["Streamlit 1.28.1<br/>- Session Management<br/>- State Management<br/>- Interactive Widgets"]
        Plotly["Plotly 5.18<br/>- Charts<br/>- Heatmaps<br/>- Visualizations"]
    end
    
    subgraph "Application Logic"
        Python["Python 3.11<br/>- Core Logic<br/>- Data Processing<br/>- Algorithms"]
        Pandas["Pandas 2.1.4<br/>- Data Manipulation<br/>- Feature Engineering<br/>- Aggregations"]
        NumPy["NumPy<br/>- Numerical Computing<br/>- Array Operations"]
    end
    
    subgraph "Data Storage"
        SQLite["SQLite 3<br/>- Relational Storage<br/>- ACID Compliance<br/>- Transaction Support"]
        AzureSDK["Azure SDK<br/>- Blob Storage<br/>- Authentication<br/>- Connection Pooling"]
    end
    
    subgraph "Infrastructure"
        Windows["Windows/Linux<br/>- Host OS<br/>- Port 8501"]
        Azure_Cloud["Azure Cloud<br/>- Blob Storage<br/>- APAC Region"]
    end
    
    Streamlit -->|Renders| Plotly
    Streamlit -->|Calls| Python
    Python -->|Uses| Pandas
    Python -->|Uses| NumPy
    Python -->|Queries| SQLite
    Python -->|Connects| AzureSDK
    SQLite -->|Runs on| Windows
    AzureSDK -->|Connects to| Azure_Cloud
```

## Integration Points

### Database Integration

```mermaid
graph TB
    subgraph "Read Operations"
        R1["mb_users<br/>- Get profile<br/>- List all users"]
        R2["learning_modules<br/>- List modules<br/>- Get assignments"]
        R3["student_daily_features<br/>- Engagement metrics<br/>- Progress data"]
    end
    
    subgraph "Write Operations"
        W1["youth_feedback_surveys<br/>- Save feedback<br/>- Store responses"]
        W2["learning_modules<br/>- Update progress<br/>- Mark complete"]
        W3["survey_distribution_logs<br/>- Track sends<br/>- Log opens"]
    end
    
    subgraph "Queries"
        Q["Feature Engineer<br/>- Compute dropout risk<br/>- Calculate sector fit<br/>- Aggregate funnel"]
    end
    
    R1 -->|Source| Q
    R2 -->|Source| Q
    R3 -->|Source| Q
    W1 -->|Target| DB["SQLite<br/>Database"]
    W2 -->|Target| DB
    W3 -->|Target| DB
    Q -->|Update| DB
```

### Azure Integration

```mermaid
graph TB
    subgraph "Azure Blob Storage"
        Container["Container: usethisone<br/>Folder: apac"]
        DS1["students.csv"]
        DS2["learning_modules.csv"]
        DS3["quiz_attempts.csv"]
        DS4["...more datasets"]
    end
    
    subgraph "Azure Connector"
        Auth["Authentication<br/>- Connection String<br/>- Access Keys"]
        Reader["Data Reader<br/>- Download Blobs<br/>- Parse CSV"]
        Cache_AZ["Caching<br/>- In-Memory<br/>- TTL"]
    end
    
    subgraph "Feature Engineer"
        FE["Feature Pipeline<br/>- Load Data<br/>- Transform<br/>- Compute Features"]
    end
    
    Container -->|Contains| DS1
    Container -->|Contains| DS2
    Container -->|Contains| DS3
    Container -->|Contains| DS4
    
    Auth -->|Connects| Container
    Reader -->|Reads| Container
    Reader -->|Caches| Cache_AZ
    FE -->|Reads| Cache_AZ
```

## Performance Considerations

### Caching Strategy

```mermaid
graph LR
    subgraph "Cache Layers"
        L1["L1: Session Cache<br/>- User Profile<br/>- TTL: 5 min<br/>- Per Session"]
        L2["L2: Feature Cache<br/>- Computed Features<br/>- TTL: 1 hour<br/>- Shared"]
        L3["L3: Dataset Cache<br/>- Raw Data<br/>- TTL: 24 hours<br/>- Blob Storage"]
    end
    
    Request["Incoming Request"]
    
    Request -->|Check| L1
    L1 -->|Miss| L2
    L2 -->|Miss| L3
    L3 -->|Miss| Compute["Compute from Source"]
    Compute -->|Store| L3
    L3 -->|Store| L2
    L2 -->|Store| L1
    L1 -->|Return| Response["Send to User"]
```

### Scalability Considerations

| Component | Current Capacity | Bottleneck | Solution |
|-----------|-----------------|-----------|----------|
| Users | 50 | Session Management | Implement session store |
| Features | 6 | Computation Time | Parallel processing |
| Queries | 100 RPS | SQLite Locks | Move to PostgreSQL |
| Azure Reads | 25+ datasets | Authentication | Use Service Principal |

---

## Deployment Architecture

### Development

```
Local Machine (Windows)
├── .venv (Python 3.11)
├── SQLite (data/mb_compass.db)
├── Streamlit (port 8501)
└── Code (Git)
```

### Production

```
Server/Cloud
├── Docker Container (Python 3.11)
├── PostgreSQL (Persistent Storage)
├── Streamlit Server (gunicorn + nginx)
├── Azure Blob (Read-Only)
└── CI/CD Pipeline (GitHub Actions)
```

---

**Last Updated**: January 29, 2026
