"""
Flask Backend Server for MovieCensorAI
Provides REST API endpoints for video processing and health checks
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Import our custom modules
from audio_utils import extract_audio, merge_audio_to_video
from whisper_transcribe import transcribe_audio
from censor_utils import detect_and_censor_audio

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'outputs'
TEMP_FOLDER = 'temp'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create necessary directories
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, TEMP_FOLDER]:
    Path(folder).mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the backend service."""
    return jsonify({
        'status': 'healthy',
        'service': 'MovieCensorAI Backend',
        'version': '1.0.0',
        'timestamp': time.time(),
        'dependencies': {
            'whisper': 'available',  # Would check actual whisper installation
            'ffmpeg': 'available',   # Would check ffmpeg installation
        }
    }), 200

@app.route('/process', methods=['POST'])
def process_video():
    """Main endpoint for processing videos with profanity censoring."""
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        censor_type = request.form.get('censor_type', 'beep')
        
        if file.filename == '' or file.filename is None:
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Supported: MP4, AVI, MOV, MKV, WebM, WMV'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        unique_filename = f"{timestamp}_{filename}"
        
        # Save uploaded file
        input_path = Path(app.config['UPLOAD_FOLDER']) / unique_filename
        file.save(str(input_path))
        
        logger.info(f"Processing file: {input_path}")
        logger.info(f"Censor type: {censor_type}")
        
        # Process the video
        output_filename = f"processed_{timestamp}_{filename}"
        output_path = Path(app.config['PROCESSED_FOLDER']) / output_filename
        
        success = process_video_pipeline(str(input_path), str(output_path), censor_type)
        
        # Clean up uploaded file
        if input_path.exists():
            input_path.unlink()
        
        if success and output_path.exists():
            # Return the processed video file
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=output_filename,
                mimetype='video/mp4'
            )
        else:
            return jsonify({'error': 'Video processing failed'}), 500
            
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

def process_video_pipeline(input_path, output_path, censor_type='beep'):
    """
    Process video through the complete censoring pipeline.
    
    Args:
        input_path (str): Path to input video file
        output_path (str): Path for output video file
        censor_type (str): Type of censoring ('beep' or 'mute')
    
    Returns:
        bool: True if processing succeeded, False otherwise
    """
    try:
        input_path = Path(input_path)
        output_path = Path(output_path)
        temp_dir = Path(TEMP_FOLDER)
        
        logger.info(f"Starting processing pipeline for {input_path}")
        
        # Step 1: Extract audio from video
        logger.info("Step 1: Extracting audio...")
        audio_path = temp_dir / f"{input_path.stem}_audio.wav"
        
        if not extract_audio(str(input_path), str(audio_path)):
            logger.error("Failed to extract audio")
            return False
        
        # Step 2: Transcribe audio using Whisper
        logger.info("Step 2: Transcribing audio with Whisper AI...")
        transcription_data = transcribe_audio(str(audio_path))
        
        if not transcription_data:
            logger.error("Failed to transcribe audio")
            return False
        
        # Step 3: Detect and censor profanity
        logger.info("Step 3: Detecting and censoring profanity...")
        censored_audio_path = temp_dir / f"{input_path.stem}_censored_audio.wav"
        
        success = detect_and_censor_audio(
            str(audio_path),
            transcription_data,
            str(censored_audio_path),
            censor_type=censor_type
        )
        
        if not success:
            logger.error("Failed to censor audio")
            return False
        
        # Step 4: Merge censored audio back to video
        logger.info("Step 4: Merging censored audio back to video...")
        success = merge_audio_to_video(
            str(input_path),
            str(censored_audio_path),
            str(output_path)
        )
        
        if not success:
            logger.error("Failed to merge audio to video")
            return False
        
        # Clean up temporary files
        for temp_file in [audio_path, censored_audio_path]:
            if temp_file.exists():
                temp_file.unlink()
        
        logger.info(f"Processing completed successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        return False

@app.route('/status', methods=['GET'])
def get_status():
    """Get current processing status and system info."""
    return jsonify({
        'active_jobs': 0,  # Would track actual jobs in production
        'queue_length': 0,
        'system_load': 'low',
        'available_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_CONTENT_LENGTH // (1024 * 1024),
        'uptime': time.time()
    })

@app.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported video formats."""
    return jsonify({
        'supported_formats': [
            {'extension': ext, 'description': f'{ext.upper()} Video'} 
            for ext in ALLOWED_EXTENSIONS
        ],
        'max_file_size': f"{MAX_CONTENT_LENGTH // (1024 * 1024)}MB"
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors."""
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎬 Starting MovieCensorAI Backend Server...")
    print(f"📁 Upload directory: {Path(UPLOAD_FOLDER).absolute()}")
    print(f"📁 Output directory: {Path(PROCESSED_FOLDER).absolute()}")
    print(f"📁 Temp directory: {Path(TEMP_FOLDER).absolute()}")
    print("🔧 Checking dependencies...")
    
    # Basic dependency check
    try:
        import whisper
        print("✅ Whisper AI available")
    except ImportError:
        print("❌ Whisper AI not found - please install: pip install openai-whisper")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg available")
        else:
            print("❌ FFmpeg not working properly")
    except FileNotFoundError:
        print("❌ FFmpeg not found - please install FFmpeg")
    
    print("🚀 Backend server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
