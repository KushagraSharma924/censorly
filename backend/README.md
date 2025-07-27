# MovieCensorAI Backend

Flask-based Python backend for AI-powered video profanity filtering.

## Features

- 🎥 Video/Audio processing with Whisper AI
- 🔍 Profanity detection and censoring
- 🛠️ RESTful API endpoints
- 📁 File upload and processing
- ⚡ Async processing with job queues

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

## API Endpoints

- `GET /health` - Health check
- `POST /process` - Process video/audio file
- `GET /status/<job_id>` - Check processing status
- `GET /formats` - Get supported formats

## Environment

- Python 3.11+
- Flask
- OpenAI Whisper
- FFmpeg

## Processing Flow

1. File upload via `/process`
2. Audio extraction with FFmpeg
3. Transcription with Whisper
4. Profanity detection and timestamping
5. Video/audio censoring
6. Return processed file
