# AI Profanity Filter - Modular Backend

A production-ready, modular Flask-based video censoring application that supports multiple processing modes including audio-based profanity filtering and future AI-based visual content detection.

## 🏗️ Modular Architecture

### Core Components

```
backend/
├── app.py                 # Main Flask application
├── video_processor.py     # Main processing orchestrator
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies
├── example_usage.py      # Usage examples
└── modules/              # Modular components
    ├── __init__.py
    ├── transcribe.py     # Whisper audio transcription
    ├── detect_words.py   # Profanity word detection
    ├── detect_nsfw.py    # NSFW visual detection (placeholder)
    └── ffmpeg_tools.py   # Video/audio processing tools
```

### Processing Pipeline

1. **Audio Extraction** → Extract audio track from video
2. **Transcription** → Convert audio to text with timestamps using Whisper
3. **Content Detection** → Detect profane words or NSFW visual content
4. **Processing** → Apply censoring (beep/mute/cut scenes)
5. **Output** → Generate final processed video

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd ai-profanity-filter/backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### Basic Usage

```python
from video_processor import process_video

# Process video with beep censoring
result = process_video(
    input_path="video.mp4",
    mode="beep"
)

print(f"Output: {result['output_path']}")
```

## 📡 API Endpoints

### Core Endpoints

- `GET /` - API information and supported modes
- `GET /health` - Health check
- `GET /modes` - Get supported processing modes
- `POST /estimate` - Estimate processing time
- `POST /process` - Process video synchronously
- `POST /process-async` - Process video asynchronously
- `GET /status/<job_id>` - Check job status
- `GET /download/<job_id>` - Download processed video

### Example API Usage

```bash
# Synchronous processing (smaller files)
curl -X POST -F "video=@test.mp4" -F "mode=beep" \
  http://localhost:5001/process

# Asynchronous processing (larger files)
curl -X POST -F "video=@large_video.mp4" -F "mode=mute" \
  http://localhost:5001/process-async

# Check status
curl http://localhost:5001/status/job-id-here

# Download result
curl -O http://localhost:5001/download/job-id-here
```

## 🎛️ Processing Modes

### Currently Available

| Mode | Description | Status |
|------|-------------|--------|
| `beep` | Replace profane words with beep sounds | ✅ Ready |
| `mute` | Replace profane words with silence | ✅ Ready |

### Coming Soon

| Mode | Description | Status |
|------|-------------|--------|
| `cut-scene` | Cut out NSFW scenes from video | 🚧 Placeholder |
| `cut-nsfw` | AI-powered NSFW content removal | 🚧 Placeholder |

## 🔧 Module Details

### `modules/transcribe.py`
- **Function**: `transcribe_with_whisper(audio_path, model_name)`
- **Purpose**: Convert audio to text with word-level timestamps
- **Models**: tiny, base, small, medium, large

```python
from modules.transcribe import transcribe_with_whisper

result = transcribe_with_whisper("audio.wav", model_name="base")
print(result['text'])
```

### `modules/detect_words.py`
- **Function**: `detect_abusive_words(transcript_data)`
- **Purpose**: Find profane words in transcript with timestamps
- **Customizable**: Add custom words via `add_custom_profanity_words()`

```python
from modules.detect_words import detect_abusive_words, add_custom_profanity_words

# Add custom words
add_custom_profanity_words(['badword1', 'badword2'])

# Detect profanity
segments = detect_abusive_words(transcript_data)
```

### `modules/detect_nsfw.py` (Placeholder)
- **Function**: `detect_nsfw_scenes(video_path, model_type)`
- **Purpose**: Detect NSFW visual content in video frames
- **Future Models**: NudeNet, Custom CNN, etc.

```python
# Future implementation
from modules.detect_nsfw import detect_nsfw_scenes

nsfw_segments = detect_nsfw_scenes("video.mp4", model_type="nudenet")
```

### `modules/ffmpeg_tools.py`
- **Functions**: `apply_beep()`, `apply_mute()`, `cut_scenes()`
- **Purpose**: Video/audio processing and censoring operations

```python
from modules.ffmpeg_tools import apply_beep, apply_mute, cut_scenes

# Apply different censoring methods
apply_beep("audio.wav", segments, "censored_beep.wav")
apply_mute("audio.wav", segments, "censored_mute.wav")
cut_scenes("video.mp4", nsfw_segments, "edited_video.mp4")
```

## 🤖 Adding AI Models

### For NSFW Detection (NudeNet)

1. **Install NudeNet**:
   ```bash
   pip install nudenet
   ```

2. **Update `modules/detect_nsfw.py`**:
   ```python
   from nudenet import NudeDetector
   
   def _detect_with_nudenet(video_path):
       detector = NudeDetector()
       frames = _extract_frames_for_analysis(video_path)
       
       detections = []
       for frame_data in frames:
           results = detector.detect(frame_data['frame'])
           # Process results and create time segments
           # ... implementation
       
       return detections
   ```

### For Custom CNN Models

1. **Install PyTorch/TensorFlow**:
   ```bash
   pip install torch torchvision
   # or
   pip install tensorflow
   ```

2. **Update `modules/detect_nsfw.py`**:
   ```python
   import torch
   
   def _detect_with_custom_cnn(video_path):
       model = torch.load('your_trained_model.pth')
       model.eval()
       
       frames = _extract_frames_for_analysis(video_path)
       detections = []
       
       for frame_data in frames:
           # Preprocess frame
           processed_frame = preprocess(frame_data['frame'])
           
           # Run inference
           with torch.no_grad():
               prediction = model(processed_frame)
           
           # Process prediction
           if prediction > threshold:
               detections.append({
                   'start': frame_data['timestamp'],
                   'end': frame_data['timestamp'] + 1.0,
                   'confidence': prediction.item(),
                   'type': 'nsfw'
               })
       
       return merge_consecutive_detections(detections)
   ```

## 📁 Directory Structure

```
backend/
├── uploads/          # Uploaded video files
├── processed/        # Processed output files
├── temp/            # Temporary processing files
└── modules/         # Modular components
```

## ⚙️ Configuration

Edit `config.py` to customize:

- File size limits
- Processing timeouts
- AI model settings
- Custom profanity words
- Logging levels

```python
# Example configuration
class Config:
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB
    DEFAULT_WHISPER_MODEL = 'base'
    NSFW_CONFIDENCE_THRESHOLD = 0.6
    CUSTOM_PROFANITY_WORDS = ['custom_word1', 'custom_word2']
```

## 🐳 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Environment Variables

```bash
export FLASK_ENV=production
export PORT=5000
export HOST=0.0.0.0
export SECRET_KEY=your-secret-key
export LOG_LEVEL=INFO
```

## 🧪 Testing

Run the example script to test functionality:

```bash
python example_usage.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your AI model integration
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the example usage script
- Review the modular architecture documentation
- Open an issue on GitHub
