# MovieCensorAI Backend

Flask-based Python backend for AI-powered video profanity filtering.

## Features

- 🎥 Video/Audio processing with Whisper AI
- 🔍 Profanity detection and censoring
- 🛠️ RESTful API endpoints
- 📁 File upload and processing
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
