# AI Profanity Filter Backend

Production-ready Flask backend for multilingual video profanity detection and censoring.

## Features

- 🎥 Video/Audio processing with OpenAI Whisper
- 🌐 Multilingual profanity detection (English, Hindi, Hinglish, Urdu)
- 🛠️ RESTful API endpoints for video processing
- 📁 Secure file upload and processing
- 🧠 Adaptive learning system
- 🔄 Real-time job tracking
- 📊 Comprehensive reporting

## Quick Start

```bash
# Setup
./setup.sh

# Run
python3 app.py
```

## API Endpoints

- `POST /api/upload` - Upload and process video
- `GET /api/status/<job_id>` - Check processing status
- `GET /api/download/<job_id>` - Download processed video
- `GET /api/health` - Health check

## Architecture

```
backend/
├── api/                    # API routes
├── services/              # Core business logic
├── utils/                 # Utility functions
├── models/                # Data models
├── data/                  # Data storage
├── training/              # Training scripts
├── app.py                 # Main application
└── config.py              # Configuration
```

## Training

Add CSV files and run training:
```bash
cd training/
python3 boom_train.py
```

## Production Deployment

1. Set environment variables:
   - `PORT` (default: 9001)
   - `FLASK_ENV` (production/development)

2. Deploy using the provided `Procfile` for platforms like Render, Heroku, etc.

## Documentation

See `ARCHITECTURE.md` for detailed system architecture and component documentation.
- ⚡ Async processing with job queues
- 🚀 Production-ready for Render deployment

## Local Setup

```bash
# Quick start
./start.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

## Render Deployment

```bash
# Push to GitHub
git add .
git commit -m "Deploy backend"
git push origin main

# Deploy to Render (see RENDER_DEPLOYMENT.md for details)
# 1. Connect GitHub repo to Render
# 2. Set root directory to 'backend'
# 3. Deploy automatically
```

## API Endpoints

- `GET /health` - Health check
- `POST /process` - Process video/audio file
- `GET /status/<job_id>` - Check processing status
- `GET /formats` - Get supported formats

## Environment

- Python 3.11+
- Flask with CORS support
- OpenAI Whisper
- FFmpeg (included in Render)
- Gunicorn for production

## Processing Flow

1. File upload via `/process`
2. Audio extraction with FFmpeg
3. Transcription with Whisper
4. Profanity detection and timestamping
5. Video/audio censoring
6. Return processed file

## Production Features

- ✅ Environment-based configuration
- ✅ Gunicorn WSGI server
- ✅ CORS enabled for frontend
- ✅ Error handling and logging
- ✅ File cleanup and management
- ✅ Health monitoring endpoints
