# AI Profanity Filter - Backend

A comprehensive SaaS platform for AI-powered video profanity detection and censoring with Supabase integration.

## 🏗️ Architecture

### Core Components
- **Flask App** (`app.py`) - Main WSGI application
- **Supabase Integration** - PostgreSQL database with real-time features
- **ML Pipeline** - Multi-model profanity detection system
- **Video Processing** - FFmpeg-based video manipulation
- **Background Jobs** - Celery-based async processing
- **REST API** - RESTful endpoints for all operations

### Tech Stack
- **Backend**: Flask 2.3.3, Python 3.9+
- **Database**: PostgreSQL via Supabase
- **Authentication**: JWT with Flask-JWT-Extended
- **Background Jobs**: Celery + Redis
- **ML/AI**: scikit-learn, transformers, whisper
- **Video Processing**: FFmpeg, moviepy
- **Deployment**: Docker, Gunicorn

## 📁 Project Structure

```
backend/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── celery_app.py              # Celery worker configuration
├── video_processor_v2.py      # Video processing pipeline
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── Dockerfile                 # Container configuration
├── Procfile                   # Deployment configuration
├──
├── api/                       # API Routes
│   ├── auth.py               # Authentication endpoints
│   ├── saas_routes.py        # SaaS platform routes
│   ├── modern_routes.py      # Modern API endpoints
│   └── routes.py             # Legacy routes
├──
├── models/                    # Data Models & ML Models
│   ├── saas_models.py        # SQLAlchemy database models
│   ├── data_models.py        # Data structure definitions
│   └── abuse_classifier.pkl  # Trained ML model
├──
├── services/                  # Business Logic
│   ├── supabase_service.py   # Supabase integration
│   ├── profanity_detection_v2.py  # Advanced profanity detection
│   ├── transcription.py      # Audio transcription service
│   ├── nsfw_detection.py     # Content moderation
│   ├── abuse_classifier.py   # ML classification
│   ├── hybrid_detector.py    # Multi-model detection
│   └── celery_worker.py      # Background task processing
├──
├── utils/                     # Utilities
│   ├── audio_utils.py        # Audio processing helpers
│   ├── censor_utils.py       # Censoring utilities
│   └── ffmpeg_tools.py       # Video manipulation tools
├──
├── training/                  # ML Training
│   ├── universal_trainer.py  # Universal model trainer
│   ├── transformer_trainer.py # Transformer model training
│   └── boom_train.py         # Rapid training scripts
├──
├── scripts/                   # Management Scripts
│   ├── start_server.py       # Production server starter
│   └── create_tables.py      # Database setup
├──
├── deployment/                # Production Configuration
│   ├── Dockerfile            # Production container
│   ├── Procfile              # Heroku deployment
│   └── runtime.txt           # Python runtime
├──
├── templates/                 # HTML Templates
├── data/                      # Training Data & Wordlists
├── instance/                  # Database Files
└── __pycache__/              # Python cache
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (via Supabase)
- Redis (for background jobs)
- FFmpeg (for video processing)

### Installation

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

4. **Start the server**:
```bash
python app.py
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
SUPABASE_DB_PASSWORD=your_db_password
SUPABASE_DB_HOST=your_db_host

# Flask Configuration
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration (Auto-configured)
DATABASE_URL=postgresql://postgres:password@host:5432/db
```

### Database Schema

The application uses Supabase PostgreSQL with the following tables:

- **users** - User accounts and profiles
- **jobs** - Video processing jobs
- **training_sessions** - ML training sessions

## 📡 API Endpoints

### Authentication
```bash
POST /api/auth/register      # User registration
POST /api/auth/login         # User login
POST /api/auth/refresh       # Token refresh
GET  /api/auth/profile       # User profile
```

### Video Processing
```bash
POST /api/v2/upload          # Upload video for processing
GET  /api/v2/jobs            # List user jobs
GET  /api/v2/jobs/{id}       # Get job details
GET  /api/v2/jobs/{id}/download  # Download processed video
```

### SaaS Platform
```bash
GET  /api/dashboard          # User dashboard data
POST /api/process            # Start video processing
GET  /api/status/{job_id}    # Check processing status
```

### Health & Monitoring
```bash
GET  /health                 # Health check
GET  /api/stats              # System statistics
```

## 🤖 ML Pipeline

### Profanity Detection Models

1. **Hybrid Detector** (`hybrid_detector.py`)
   - Combines multiple detection methods
   - Word-list based detection
   - ML-based classification
   - Context-aware analysis

2. **Transformer Classifier** (`transformer_classifier.py`)
   - BERT-based classification
   - Contextual understanding
   - Fine-tuned for profanity detection

3. **Abuse Classifier** (`abuse_classifier.py`)
   - scikit-learn based model
   - Feature engineering
   - Lightweight and fast

### Video Processing Pipeline

```python
# Video Processing Flow
Input Video → Audio Extraction → Transcription → 
Profanity Detection → Timeline Generation → 
Video Censoring → Output Video
```

## 🔄 Background Jobs

### Celery Workers

```bash
# Start Celery worker
celery -A celery_app.celery worker --loglevel=info

# Start Celery beat (scheduler)
celery -A celery_app.celery beat --loglevel=info
```

### Job Types
- Video processing jobs
- ML model training
- Data preprocessing
- Cleanup tasks

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t ai-profanity-filter .

# Run container
docker run -p 8080:8080 ai-profanity-filter

# Using docker-compose
docker-compose up
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app

# Or use the production script
python scripts/start_server.py
```

## 📊 Monitoring & Logging

### Logging Configuration
- **Level**: INFO (configurable)
- **Format**: Timestamp, module, level, message
- **Output**: Console and file rotation

### Health Checks
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "AI Profanity Filter SaaS Platform is running",
  "version": "2.0.0",
  "environment": "production"
}
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# API tests
python -m pytest tests/api/
```

### Test Coverage
```bash
coverage run -m pytest
coverage report
coverage html
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection**:
```bash
# Check Supabase connection
python -c "from services.supabase_service import supabase_service; print(supabase_service.test_connection())"
```

2. **ML Model Loading**:
```bash
# Verify models exist
ls -la models/
python -c "from services.abuse_classifier import load_classifier; load_classifier()"
```

3. **Video Processing**:
```bash
# Check FFmpeg installation
ffmpeg -version
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## 📈 Performance Optimization

### Database Optimization
- Connection pooling via SQLAlchemy
- Query optimization with indexes
- Supabase real-time subscriptions

### ML Model Optimization
- Model caching and lazy loading
- Batch processing for multiple videos
- GPU acceleration (when available)

### Video Processing
- FFmpeg hardware acceleration
- Parallel processing for segments
- Optimized encoding settings

## 🛠️ Development

### Development Server
```bash
# Hot reload development server
flask run --debug --host=0.0.0.0 --port=8080
```

### Code Quality
```bash
# Linting
flake8 .
black .
isort .

# Type checking
mypy .
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Add unit tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- GitHub Issues: [Create an issue](https://github.com/KushagraSharma924/ai-profanity-filter/issues)
- Documentation: [Wiki](https://github.com/KushagraSharma924/ai-profanity-filter/wiki)

---

**Built with ❤️ for content creators and platform safety**
