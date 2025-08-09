# AI Profanity Filter SaaS Platform

A production-ready, multilingual profanity detection and video content filtering platform with advanced AI capabilities.

## 🚀 Features

### Core Capabilities
- **Multilingual Detection**: English, Hindi (Devanagari), and Hinglish (Romanized) support
- **Hybrid AI Engine**: Combines transformer models with keyword-based detection
- **Video Processing**: Real-time video profanity detection and censoring
- **NSFW Content Detection**: Advanced image/video content filtering
- **Audio Transcription**: Whisper-based speech-to-text processing

### SaaS Platform Features
- **JWT Authentication**: Secure user authentication and authorization
- **API Key Management**: Programmatic access control
- **Subscription Billing**: Tiered pricing with usage tracking
- **Real-time Processing**: Background job processing with Celery
- **RESTful API**: Comprehensive v2 API endpoints
- **Dashboard UI**: User-friendly web interface

## 🏗️ Architecture

### Backend Stack
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **Celery**: Distributed task queue
- **JWT**: Authentication tokens
- **Supabase**: Cloud database

### AI/ML Stack
- **Transformers**: Hugging Face models for text classification
- **Whisper**: OpenAI speech recognition
- **NSFW Detection**: Computer vision models
- **Hybrid Detection**: Ensemble keyword + transformer approach

### Frontend Stack
- **React**: Modern UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tooling
- **Tailwind CSS**: Utility-first styling

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis (for Celery)
- FFmpeg (for video processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KushagraSharma924/ai-profanity-filter.git
   cd ai-profanity-filter
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your configuration
   ```

### Running the Application

**Development Mode:**
```bash
# Start all services
./start.sh
```

This starts:
- Backend API server (Port 8080)
- Frontend development server (Port 3000)
- Celery worker for background tasks

**Production Mode:**
```bash
# Backend only
cd backend && python3 app.py

# With production WSGI
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh

### Content Detection Endpoints
- `POST /api/v2/detect-text` - Single text abuse detection
- `POST /api/v2/detect-batch` - Batch text processing
- `POST /api/v2/process-video` - Video content filtering

### Job Management
- `GET /api/v2/jobs` - List user jobs
- `GET /api/v2/job/{id}` - Get job status
- `GET /api/v2/job/{id}/download` - Download processed content

### Subscription & Billing
- `GET /api/subscription/status` - Current subscription
- `POST /api/subscription/upgrade` - Upgrade plan
- `GET /api/usage/stats` - Usage statistics

## 🔧 Configuration

### Environment Variables

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
DATABASE_URL=your_database_url

# Authentication
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES=3600

# AI Models
TRANSFORMER_MODEL_PATH=./models/abuse_classifier.pkl
WHISPER_MODEL_SIZE=base
NSFW_MODEL_PATH=./models/nsfw_detector

# External Services
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379

# API Configuration
CORS_ORIGINS=http://localhost:3000,https://censorly.vercel.app
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## 🎯 Usage Examples

### Text Detection
```python
import requests

response = requests.post('http://localhost:8080/api/v2/detect-text', 
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'},
    json={'text': 'Your text to analyze'}
)

result = response.json()
print(f"Is abusive: {result['result']['is_abusive']}")
print(f"Detected words: {result['result']['detected_words']}")
```

### Video Processing
```python
files = {'video': open('video.mp4', 'rb')}
data = {
    'censor_mode': 'beep',
    'language': 'en',
    'sensitivity': 'high'
}

response = requests.post('http://localhost:8080/api/v2/process-video',
    headers={'Authorization': 'Bearer YOUR_JWT_TOKEN'},
    files=files,
    data=data
)

job_id = response.json()['job_id']
# Poll for completion...
```

## 🛠️ Development

### Project Structure
```
ai-profanity-filter/
├── backend/
│   ├── api/          # API routes and blueprints
│   ├── models/       # Database models and AI models
│   ├── services/     # Business logic and AI services
│   ├── utils/        # Helper utilities
│   ├── training/     # ML model training scripts
│   └── app.py        # Flask application entry point
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/      # Page components
│   │   ├── hooks/      # Custom React hooks
│   │   └── lib/        # Utility libraries
│   └── package.json
└── start.sh          # Development startup script
```

### Adding New Features

1. **Backend API Endpoint**:
   - Add route to appropriate blueprint in `backend/api/`
   - Implement business logic in `backend/services/`
   - Add database models if needed in `backend/models/`

2. **Frontend Component**:
   - Create component in `frontend/src/components/`
   - Add routing in main App component
   - Implement API calls using hooks

3. **AI/ML Integration**:
   - Add model files to `backend/models/`
   - Implement detection logic in `backend/services/`
   - Add training scripts to `backend/training/`

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Health check
curl http://localhost:8080/health

# Test detection (requires auth)
curl -X POST http://localhost:8080/api/v2/detect-text \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"text": "Test message"}'
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment
1. Set up production environment variables
2. Install dependencies on server
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure process manager (PM2/systemd)

### Environment-Specific Configs
- **Development**: Debug enabled, hot reload
- **Staging**: Production-like with test data
- **Production**: Optimized, secure, monitored

## 📊 Monitoring & Analytics

### Metrics Tracked
- API request rates and response times
- Detection accuracy and false positives
- User engagement and feature usage
- System resource utilization
- Error rates and types

### Health Monitoring
- Database connection status
- AI model availability
- Background job queue status
- External service dependencies

## 🔒 Security

### Authentication & Authorization
- JWT-based stateless authentication
- API key management for programmatic access
- Role-based access control (RBAC)
- Rate limiting and request throttling

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- Secure file upload handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests for new features
- Update documentation for API changes
- Follow semantic versioning for releases

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- API Documentation: `/api/docs`
- User Guide: Available in the dashboard
- Developer Guide: This README

### Community
- GitHub Issues: Bug reports and feature requests
- Discussions: Community support and questions

### Commercial Support
- Enterprise licensing available
- Custom model training services
- Priority support and SLA options

---

**Built with ❤️ for safer digital content**
