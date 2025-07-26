# ai-profanity-filter

🎬 **ai-profanity-filter** - An AI-powered tool to detect and censor abusive words from movies and videos.

## Features

1. **Audio Extraction**: Extract audio from video files using ffmpeg
2. **AI Transcription**: Transcribe audio using OpenAI Whisper with word-level timestamps
3. **Profanity Detection**: Detect abusive words using the better-profanity library
4. **Smart Censoring**: Replace offensive audio segments with beep sounds or mute them
5. **Video Reconstruction**: Merge cleaned audio back into the original video

## Tech Stack

- **Python 3.11+** (recommended for full compatibility)
- **OpenAI Whisper** - For speech-to-text transcription
- **FFmpeg** - For audio/video processing
- **better-profanity** - For profanity detection
- **pydub** - For audio manipulation

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
