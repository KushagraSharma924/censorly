# AI Profanity Filter - Production SaaS Platform

A production-ready AI-powered profanity and abuse detection system for video content with real-time ML classification.

## 🚀 Features

- **ML-Powered Detection**: Real scikit-learn based abuse classification
- **Video Processing**: Automated video content moderation  
- **Multi-User SaaS**: JWT authentication with API key support
- **Production Ready**: Docker deployment, background processing
- **Modern API**: RESTful v2 API with confidence scoring
- **Real-time Processing**: Background job management with Celery

## 🏗️ Architecture

```
backend/
├── api/                 # API routes and authentication
├── models/             # ML models and data models  
├── services/           # Core business logic
├── utils/              # Utility functions
├── scripts/            # Setup and deployment scripts
├── deployment/         # Docker and production files
├── tools/              # Development and testing tools
└── training/           # ML model training
```

## 🚦 Quick Start

### 1. Production Setup
```bash
cd backend
python scripts/setup_production.py
```

### 2. Start Server
```bash
cd backend  
python scripts/start_server.py
```

### 3. Test API
```bash
curl http://localhost:8080/api/v2/health
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/health` | GET | System health check |
| `/api/v2/test-classifier` | POST | Test abuse classification |
| `/api/v2/process-video` | POST | Process video content |
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User authentication |

## 🔧 Configuration

- **Port**: 8080 (configurable via PORT env var)
- **Database**: SQLite (production ready)
- **ML Model**: Scikit-learn pipeline with TF-IDF
- **Authentication**: JWT + API keys

## 📈 Production Status

✅ ML Model Active  
✅ Authentication System  
✅ Database Initialized  
✅ Background Processing  
✅ Production Configuration  

**Ready for immediate deployment!**