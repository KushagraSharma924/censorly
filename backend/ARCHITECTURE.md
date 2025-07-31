# AI Profanity Filter - Backend Architecture

## Overview
The backend has been successfully refactored into a clean, modular architecture following Python best practices. The system now supports multilingual profanity detection (English, Hindi Latin, Hindi Devanagari, and Urdu/Arabic scripts) with a robust Flask API.

## Folder Structure

```
backend/
├── api/                     # Flask API routes and endpoints
│   ├── __init__.py
│   └── routes.py           # All API route handlers
├── services/               # Core business logic services
│   ├── __init__.py
│   ├── transcription.py    # Whisper audio transcription
│   ├── profanity_detection.py  # Multilingual profanity detection
│   └── nsfw_detection.py   # Visual content detection (placeholder)
├── utils/                  # Utility functions and helpers
│   ├── __init__.py
│   ├── audio_utils.py      # Audio extraction and processing
│   ├── censor_utils.py     # Audio censoring utilities
│   ├── ffmpeg_tools.py     # FFmpeg wrapper functions
│   └── setup.py           # Environment setup utilities
├── models/                 # Data models and configurations
│   ├── __init__.py
│   └── data_models.py      # Dataclasses for video processing
├── data/                   # Data storage
│   └── wordlists/          # Profanity word lists and learned words
│       └── learned_words.json
├── uploads/                # Uploaded video files
├── processed/              # Processed video outputs
├── logs/                   # Application logs
├── app.py                  # Main Flask application entry point
├── main.py                 # CLI interface for video processing
├── video_processor.py      # Main video processing orchestrator
├── config.py              # Application configuration
└── requirements.txt       # Python dependencies
```

## Key Components

### Services Layer
- **Transcription Service**: Handles Whisper audio transcription with automatic model selection
- **Profanity Detection Service**: Multilingual word detection with adaptive learning
- **NSFW Detection Service**: Placeholder for visual content detection

### Utils Layer
- **Audio Utils**: Audio extraction and merging using FFmpeg
- **Censor Utils**: Audio censoring with beep/mute functionality
- **FFmpeg Tools**: Video processing utilities
- **Setup Utils**: Environment validation and logging setup

### Models Layer
- **Data Models**: Typed data structures for video processing results
- **Video Segment**: Base class for timed video segments
- **Profane Segment**: Profanity-specific segment with metadata
- **Processing Job**: Job tracking and status management
- **Processing Result**: Complete processing results with statistics

### API Layer
- **Routes**: RESTful API endpoints for video upload, processing, and download
- **Job Management**: Asynchronous processing with status tracking
- **File Handling**: Secure file upload and download

## Features

### Multilingual Support
- **English**: Comprehensive profanity word list with variants
- **Hindi Latin**: Transliterated Hindi abusive words
- **Hindi Devanagari**: Native script Hindi words
- **Urdu/Arabic**: Script-specific word detection

### Processing Modes
- **Beep**: Replace profane audio with beep sounds
- **Mute**: Replace profane audio with silence
- **Cut-scene**: Remove entire scenes (planned)
- **Cut-nsfw**: Remove NSFW content (planned)

### Advanced Features
- **Adaptive Learning**: System learns from missed detections
- **Automatic Model Selection**: Uses optimal Whisper model per language
- **Real-time Job Tracking**: WebSocket-style job status updates
- **File Cleanup**: Automatic cleanup of old processed files
- **Error Handling**: Comprehensive error reporting and logging

## API Endpoints

```
GET  /api/health           - Health check and system status
POST /api/upload           - Upload and process video
GET  /api/status/<job_id>  - Get processing job status
GET  /api/download/<job_id> - Download processed video
GET  /api/jobs             - List all processing jobs
GET  /api/modes            - Get supported processing modes
DELETE /api/cleanup/<job_id> - Clean up job files
```

## Usage

### Starting the Server
```bash
python3 app.py
```

### CLI Processing
```bash
python3 main.py input_video.mp4 --output censored_video.mp4
```

### Running with Tasks
Use VS Code tasks to start the backend server in background mode.

## Configuration

The system uses environment variables and config files for:
- Flask settings (secret key, upload limits)
- CORS origins for frontend integration
- Processing directories and cleanup policies
- Logging levels and file output
- Whisper model preferences

## Dependencies

Core dependencies include:
- **whisper**: OpenAI Whisper for audio transcription
- **torch**: PyTorch for AI models
- **ffmpeg-python**: Video/audio processing
- **flask**: Web framework
- **flask-cors**: Cross-origin resource sharing
- **pydub**: Audio manipulation
- **better-profanity**: Text profanity filtering

## Performance Optimizations

- Automatic Whisper model selection (base for most languages, medium for Hindi)
- Background processing with job queuing
- Efficient audio extraction and merging
- Memory-conscious video processing
- Cleanup utilities for disk space management

## Testing

The import structure has been validated and all modules can be imported successfully. The system supports:
- Unit testing of individual services
- Integration testing of the complete pipeline
- API testing with various file formats
- Performance testing with large video files

## Future Enhancements

- Visual NSFW content detection using AI models
- Real-time streaming processing
- Multi-language UI support
- Advanced analytics and reporting
- Custom model training interfaces
- Distributed processing support
