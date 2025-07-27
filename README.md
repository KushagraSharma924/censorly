# MovieCensorAI 🎬

A production-ready SaaS platform for AI-powered video profanity filtering with modern web interface and payment integration.

## 🚀 Live Demo

**Frontend:** Modern SaaS interface with real-time processing  
**Backend:** Flask API with Whisper AI integration  
**Payment:** Fullscreen Razorpay checkout experience

## ✨ Features

### 🎯 **Core AI Processing**
- OpenAI Whisper for accurate speech-to-text
- Smart profanity detection and censoring
- Video/audio file processing
- Real-time status monitoring

### 💻 **SaaS Platform**
- Professional web interface
- REST API architecture
- Real-time health monitoring
- File upload with validation
- Processing queue management

### 💳 **Payment Integration**
- Razorpay fullscreen checkout
- Multiple pricing tiers (Free/Pro/Enterprise)
- No customer form required
- Payment verification system

### 🛠️ **Production Ready**
- Node.js/Express frontend
- Flask Python backend
- Environment-based configuration
- Professional UI/UX design

## 📁 Project Structure

```
├── frontend/              # Node.js/Express SaaS Platform
│   ├── app.js            # Main API server
│   ├── package.json      # Dependencies
│   ├── public/           # Static assets
│   │   ├── css/          # Tailwind CSS styles
│   │   └── js/           # Frontend JavaScript
│   └── views/            # EJS templates
├── backend/              # Python Flask API
│   ├── server.py         # Main Flask server
│   ├── requirements.txt  # Python dependencies
│   ├── audio_utils.py    # Audio processing
│   ├── censor_utils.py   # Censoring logic
│   ├── whisper_transcribe.py # AI transcription
│   └── outputs/          # Processed files
└── README.md             # This file
```

## 🚀 Quick Start

### Frontend (SaaS Interface)
```bash
cd frontend
npm install
npm start
# Access: http://localhost:3000
```

### Backend (Processing API)
```bash
cd backend
pip install -r requirements.txt
python server.py
# API: http://localhost:5000
```

## 🔧 Configuration

### Environment Variables
Create `frontend/.env`:
```env
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### API Endpoints

**Frontend APIs:**
- `GET /api/health` - System health
- `GET /api/stats` - Platform statistics  
- `GET /api/pricing` - Pricing plans
- `POST /api/contact` - Contact form
- `POST /api/create-order` - Payment orders

**Backend APIs:**
- `POST /process` - File processing
- `GET /status/<job_id>` - Processing status
- `GET /formats` - Supported formats

## Installation

1. Clone or download this repository
2. **Install Python 3.11** (recommended for full compatibility):
   - **macOS**: `brew install python@3.11`
   - **Ubuntu/Debian**: `sudo apt install python3.11 python3.11-venv`
   - **Windows**: Download from https://www.python.org/downloads/
3. Create a virtual environment with Python 3.11:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Make sure you have **ffmpeg** installed on your system:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from https://ffmpeg.org/

**Note**: While the project may work with Python 3.13+, Python 3.11 is recommended for optimal compatibility with all audio processing libraries.

## Usage

### Basic Usage

```bash
python main.py input_video.mp4
```

This will create a censored version in the `outputs/` directory with the name `censored_input_video.mp4`.

### Advanced Usage

```bash
python main.py input_video.mp4 --output my_clean_video.mp4 --temp-dir temp_files
```

### Command Line Options

- `input_video`: Path to the input video file (required)
- `--output`, `-o`: Custom output filename (optional)
- `--temp-dir`: Custom temporary directory for processing files (default: temp)

## Project Structure

```
ai-profanity-filter/
├── main.py              # Main orchestration script
├── audio_utils.py       # Audio extraction and merging utilities
├── whisper_transcribe.py # Whisper transcription functionality
├── censor_utils.py      # Profanity detection and audio censoring
├── test_components.py   # Test script for components
├── requirements.txt     # Python dependencies
├── outputs/            # Output directory for processed videos
└── README.md           # This file
```

## How It Works

1. **Extract Audio**: The video's audio track is extracted as a WAV file
2. **Transcribe**: OpenAI Whisper transcribes the audio with precise word-level timestamps
3. **Detect Profanity**: The better-profanity library scans the transcript for offensive words
4. **Censor Audio**: Identified segments are replaced with beep sounds using pydub
5. **Merge Back**: The cleaned audio is merged back with the original video using ffmpeg

## Testing

Run the test script to verify all components work correctly:

```bash
python test_components.py
```

## Supported Video Formats

- MP4, AVI, MOV, MKV, WMV
- Any format supported by ffmpeg

## Customization

### Adding Custom Profanity Words

Edit `censor_utils.py` and use the `add_custom_profanity_words()` function:

```python
from censor_utils import add_custom_profanity_words
add_custom_profanity_words(["word1", "word2", "word3"])
```

### Changing Whisper Model

Modify the model in `whisper_transcribe.py`. Available models:
- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: Even better accuracy
- `large`: Best accuracy, slowest

### Censoring Options

In `censor_utils.py`, you can change the censoring method:
- `"beep"`: Replace with beep sound (default)
- `"mute"`: Replace with silence

## Limitations

- Processing time depends on video length and Whisper model size
- Requires sufficient disk space for temporary files
- Accuracy depends on audio quality and Whisper model
- May not detect context-dependent profanity

## Contributing

Feel free to submit issues and pull requests to improve ai-profanity-filter!

## License

This project is open source. Please check individual library licenses for their respective terms.
