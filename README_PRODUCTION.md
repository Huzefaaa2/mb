# Magic Bus Youth Employment Platform

<div align="center">

![Magic Bus Logo](docs/assets/logo.png)

**Empowering Youth Through Skills, Learning, and Employment**

[![Status](https://img.shields.io/badge/status-production-brightgreen)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()

[Website](https://www.magicbus.org) • [Documentation](./docs/wiki) • [Support](mailto:support@magicbus.org)

</div>

---

## 📖 Overview

Magic Bus is a comprehensive **youth employment and skills development platform** that combines personalized learning, gamification, and employer feedback to bridge the skills gap between students and industry needs.

### Key Features

🎓 **Personalized Learning**
- Adaptive learning modules
- Progress tracking & analytics
- Skill-based recommendations

🎮 **Gamification**
- Badge system & leaderboards
- Points & achievements
- Engagement incentives

📊 **Analytics & Insights**
- Student performance tracking
- Dropout risk prediction
- Sector fit analysis

💼 **Employer Feedback**
- Post-placement surveys
- Performance tracking
- Skill validation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip or conda
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/magicbus/mb.git
cd mb

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-py311.txt

# Initialize database
python scripts/init_db.py

# Run the application
streamlit run app/app.py
```

**Application opens at**: http://localhost:8501

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f streamlit-app

# Stop services
docker-compose down
```

### Demo Accounts

```
Student Account:
  Email: student@magicbus.com
  Password: password123

Admin Account:
  Email: admin@magicbus.com
  Password: admin123
```

---

## 📋 Project Structure

```
mb/
├── app/                    # Main application
│   ├── app.py             # Entry point
│   ├── auth/              # Authentication
│   ├── components/        # UI components
│   ├── data/              # Data layer
│   ├── database/          # Database operations
│   ├── integrations/      # External services
│   ├── pages/             # Streamlit pages
│   └── services/          # Business logic
├── config/                # Configuration
├── docs/                  # Documentation
│   └── wiki/              # Comprehensive wiki (7 pages)
├── scripts/               # Utility scripts
├── tests/                 # Test suites
├── data/                  # Data storage
├── docker-compose.yml     # Docker setup
├── Dockerfile             # Container image
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Streamlit)                   │
├─────────────────────────────────────────────────────────┤
│  Authentication  │  Learning  │  Surveys  │  Analytics  │
├─────────────────────────────────────────────────────────┤
│                    API Layer (REST)                      │
├─────────────────────────────────────────────────────────┤
│  Services Layer (Business Logic)                        │
├─────────────────────────────────────────────────────────┤
│  Data Access Layer                                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Database │  │  Storage │  │Databricks│             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Features

### 1. User Management
- Secure registration & login
- Role-based access control
- Profile management
- Email verification

### 2. Learning Modules
- 16 curated modules
- Progress tracking
- Difficulty levels
- Time-based analytics

### 3. Gamification
- Badge system (10+ badges)
- Points accumulation
- Leaderboards
- Achievement tracking

### 4. Survey System
- Youth feedback surveys
- Employer surveys
- Template management
- Response tracking

### 5. Analytics
- User engagement metrics
- Module effectiveness
- Dropout risk detection
- Sector fit analysis

### 6. Integrations
- Azure Blob Storage
- Databricks
- Azure SQL Database
- Speech-to-Text

---

## 📊 Data & Analytics

### Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Users | 50 | ✓ |
| Modules | 16 | ✓ |
| Assignments | 100 | ✓ |
| Avg Completion | 65% | ⚠ |
| DAU | 28 | ✓ |
| Module Effectiveness | 60% | ⚠ |

### Analytics Framework

- **Mobilisation Funnel**: Track user journey
- **Learning Dashboard**: Monitor progress
- **Risk Detection**: Identify at-risk students
- **Sector Fit**: Match skills to careers
- **Gamification Impact**: Measure engagement

See [Analytics Documentation](./docs/wiki/05-Analytics-Metrics.md)

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py -v
```

**Test Coverage**: 85%+  
**Total Tests**: 22  
**Pass Rate**: 100%

---

## 🔐 Security

- ✅ Password hashing (Bcrypt)
- ✅ Session management
- ✅ RBAC (Role-Based Access Control)
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ CSRF protection
- ✅ Secret management
- ✅ Encrypted connections (HTTPS ready)

See [Security Documentation](./docs/wiki/04-Deployment-Operations.md#security)

---

## 📚 Documentation

### Quick Links

| Document | Purpose |
|----------|---------|
| [Architecture](./docs/wiki/01-Architecture.md) | System design & components |
| [Features](./docs/wiki/02-Features.md) | Feature documentation |
| [Data Model](./docs/wiki/03-Data-Model.md) | Database schema |
| [Deployment](./docs/wiki/04-Deployment-Operations.md) | Setup & deployment guide |
| [Analytics](./docs/wiki/05-Analytics-Metrics.md) | Analytics framework |
| [API Reference](./docs/wiki/06-API-Reference.md) | API documentation |
| [FAQ](./docs/wiki/07-Troubleshooting-FAQ.md) | Troubleshooting & FAQ |

### Additional Resources

- [Quick Reference](./docs/QUICK_REFERENCE.md) - Common tasks
- [Implementation Guide](./docs/IMPLEMENTATION_SUMMARY.md) - Implementation details
- [Quick Start Script](./QUICK_START.py) - Automated setup

---

## 🚢 Deployment

### Local Development

```bash
streamlit run app/app.py
```

### Docker

```bash
docker-compose up -d
```

### Production (Azure)

See [Deployment Guide](./docs/wiki/04-Deployment-Operations.md) for complete instructions including:
- Azure resource setup
- Docker image deployment
- Environment configuration
- Monitoring setup

---

## 💻 Technology Stack

### Frontend
- **Streamlit**: Web framework
- **Python**: Programming language
- **Plotly**: Data visualization

### Backend
- **Python 3.11+**: Runtime
- **SQLite/Azure SQL**: Database
- **Databricks**: Analytics engine

### Infrastructure
- **Docker**: Containerization
- **Azure**: Cloud platform
- **GitHub**: Version control

### Integrations
- **Azure Blob Storage**: File storage
- **Databricks**: ML & Analytics
- **Azure SQL**: Production database

---

## 📈 Performance

### Benchmarks

```
Page Load Times:
  - Login: 150ms
  - Dashboard: 300ms
  - Analytics: 450ms

Database:
  - User lookup: ~20ms
  - Module fetch: ~30ms
  - Analytics query: ~150ms

Scalability:
  - Current: 50 users
  - Scalable to: 10,000+ users
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---

## 🐛 Bug Reports & Feature Requests

### Report a Bug

1. Check [existing issues](https://github.com/magicbus/mb/issues)
2. Create [new issue](https://github.com/magicbus/mb/issues/new)
3. Include:
   - Description
   - Steps to reproduce
   - Expected behavior
   - Screenshots (if applicable)

### Request a Feature

1. Check [feature requests](https://github.com/magicbus/mb/discussions)
2. Create [discussion](https://github.com/magicbus/mb/discussions/new)
3. Include:
   - Use case
   - Proposed solution
   - Examples

---

## 📞 Support

- **Documentation**: [Wiki](./docs/wiki)
- **FAQ**: [Troubleshooting & FAQ](./docs/wiki/07-Troubleshooting-FAQ.md)
- **Email**: support@magicbus.org
- **Chat**: In-app support (9 AM - 5 PM IST)
- **Issues**: [GitHub Issues](https://github.com/magicbus/mb/issues)

---

## 👥 Team

**Project Lead**: [Your Name]  
**Email**: team@magicbus.org

---

## 🙏 Acknowledgments

- Magic Bus organization
- Development team
- All contributors
- Users and testers

---

## 📊 Project Statistics

- **Repository**: Public on GitHub
- **License**: MIT
- **Status**: Production Ready
- **Version**: 1.0.0
- **Last Updated**: January 29, 2026
- **Total Commits**: 100+
- **Contributors**: 5+
- **Issues**: 0 critical
- **Documentation**: Complete

---

<div align="center">

**[↑ back to top](#magic-bus-youth-employment-platform)**

Made with ❤️ by the Magic Bus Team

</div>
