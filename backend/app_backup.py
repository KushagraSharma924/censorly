#!/usr/bin/env python3
"""
AI Profanity Filter - Refactored Flask Backend
Production-ready modular video processing API with support for multiple censoring modes.
"""

import os
import sys
import tempfile
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Import our modular video processor
from video_processor import process_video, get_supported_modes, estimate_processing_time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS to allow frontend communication
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:8080', 'http://127.0.0.1:8080'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Disposition'],
     supports_credentials=True)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max file size
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv', 'm4v'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Job tracking for async processing (in production, use Redis or database)
active_jobs = {}
job_results = {}


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def background_process_video(job_id, input_path, mode, custom_words=None):
    """
    Background function to process video asynchronously.
    
    Args:
        job_id: Unique job identifier
        input_path: Path to input video file
        mode: Processing mode
        custom_words: Optional custom profanity words
    """
    try:
        logger.info(f"Starting background processing for job {job_id}")
        active_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'start_time': time.time(),
            'message': 'Starting video processing...'
        }
        
        # Process the video
        result = process_video(
            input_path=input_path,
            mode=mode,
            custom_words=custom_words
        )
        
        # Store successful result
        job_results[job_id] = {
            'status': 'completed',
            'progress': 100,
            'result': result,
            'end_time': time.time(),
            'message': 'Video processing completed successfully!'
        }
        
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job {job_id} failed: {error_msg}")
        
        # Store error result
        job_results[job_id] = {
            'status': 'failed',
            'progress': 0,
            'error': error_msg,
            'end_time': time.time(),
            'message': f'Processing failed: {error_msg}'
        }
        
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]
        
        # Clean up input file on error
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except:
            pass


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API information."""
    return jsonify({
        'service': 'AI Profanity Filter Backend',
        'version': '2.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'description': 'Modular video processing API with support for audio censoring and visual content filtering',
        'endpoints': {
            'health': '/health',
            'process': '/process (POST)',
            'process_async': '/process-async (POST)', 
            'status': '/status/<job_id> (GET)',
            'download': '/download/<job_id> (GET)',
            'modes': '/modes (GET)',
            'estimate': '/estimate (POST)'
        },
        'supported_modes': get_supported_modes(),
        'documentation': 'https://github.com/yourusername/ai-profanity-filter'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Profanity Filter Backend',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'python_version': sys.version,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'active_jobs': len(active_jobs),
        'completed_jobs': len(job_results)
    })


@app.route('/modes', methods=['GET'])
def get_modes():
    """Get supported processing modes."""
    return jsonify({
        'supported_modes': get_supported_modes(),
        'total_modes': len(get_supported_modes()),
        'ready_modes': [mode for mode in get_supported_modes() if mode.get('ready', False)]
    })


@app.route('/estimate', methods=['POST'])
def estimate_processing():
    """Estimate processing time for a video file."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        mode = request.form.get('mode', 'beep')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Save file temporarily for estimation
        temp_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{temp_id}_{filename}")
        file.save(temp_path)
        
        try:
            # Get estimation
            estimation = estimate_processing_time(temp_path, mode)
            
            # Clean up temp file
            os.remove(temp_path)
            
            return jsonify({
                'estimation': estimation,
                'filename': filename,
                'mode': mode
            })
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
        
    except Exception as e:
        logger.error(f"Estimation error: {str(e)}")
        return jsonify({'error': f'Estimation failed: {str(e)}'}), 500


@app.route('/process', methods=['POST'])
def process_video_sync():
    """Process video synchronously (for smaller files)."""
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        mode = request.form.get('mode', 'beep')
        custom_words = request.form.get('custom_words', '').split(',') if request.form.get('custom_words') else None
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'File type not supported',
                'supported_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        if mode not in ['beep', 'mute', 'cut-scene', 'cut-nsfw']:
            return jsonify({
                'error': 'Invalid mode',
                'supported_modes': [m['mode'] for m in get_supported_modes()]
            }), 400
        
        # Generate unique filename
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        
        input_filename = f"{job_id}_input{ext}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File saved: {input_path}")
        
        try:
            # Process the video
            result = process_video(
                input_path=input_path,
                mode=mode,
                custom_words=custom_words
            )
            
            # Clean up input file
            os.remove(input_path)
            
            # Return the processed video file with proper headers
            if result['output_path'] and os.path.exists(result['output_path']):
                response = send_file(
                    result['output_path'],
                    as_attachment=True,
                    download_name=f"processed_{filename}",
                    mimetype='video/mp4'
                )
                
                # Add headers for CORS and file handling
                response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                
                return response
            else:
                return jsonify({'error': 'Processing completed but output file not found'}), 500
            
        except Exception as e:
            # Clean up input file on error
            if os.path.exists(input_path):
                os.remove(input_path)
            raise e
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/process-async', methods=['POST'])
def process_video_async():
    """Process video asynchronously (for larger files)."""
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        mode = request.form.get('mode', 'beep')
        custom_words = request.form.get('custom_words', '').split(',') if request.form.get('custom_words') else None
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'File type not supported',
                'supported_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        if mode not in ['beep', 'mute', 'cut-scene', 'cut-nsfw']:
            return jsonify({
                'error': 'Invalid mode',
                'supported_modes': [m['mode'] for m in get_supported_modes()]
            }), 400
        
        # Generate unique job ID and filename
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        
        input_filename = f"{job_id}_input{ext}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File saved for async processing: {input_path}")
        
        # Start background processing
        thread = threading.Thread(
            target=background_process_video,
            args=(job_id, input_path, mode, custom_words)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Video processing started. Use /status/<job_id> to check progress.',
            'filename': filename,
            'mode': mode,
            'status_url': f'/status/{job_id}',
            'download_url': f'/download/{job_id}'
        }), 202
        
    except Exception as e:
        logger.error(f"Async processing error: {str(e)}")
        return jsonify({'error': f'Failed to start processing: {str(e)}'}), 500


@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get processing status for a job."""
    try:
        # Check active jobs first
        if job_id in active_jobs:
            job_info = active_jobs[job_id].copy()
            job_info['job_id'] = job_id
            return jsonify(job_info)
        
        # Check completed jobs
        if job_id in job_results:
            job_info = job_results[job_id].copy()
            job_info['job_id'] = job_id
            return jsonify(job_info)
        
        # Job not found
        return jsonify({
            'job_id': job_id,
            'status': 'not_found',
            'message': 'Job ID not found. It may have expired or never existed.'
        }), 404
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500


@app.route('/download/<job_id>', methods=['GET'])
def download_result(job_id):
    """Download the processed video for a completed job."""
    try:
        # Check if job is completed
        if job_id not in job_results:
            return jsonify({
                'error': 'Job not found or not completed',
                'job_id': job_id
            }), 404
        
        job_result = job_results[job_id]
        
        if job_result['status'] != 'completed':
            return jsonify({
                'error': 'Job not completed',
                'status': job_result['status']
            }), 400
        
        output_path = job_result['result']['output_path']
        
        if not output_path or not os.path.exists(output_path):
            return jsonify({'error': 'Output file not found'}), 404
        
        # Generate download filename
        original_name = Path(job_result['result']['input_path']).name
        mode = job_result['result']['mode']
        download_name = f"processed_{mode}_{original_name}"
        
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='video/mp4'
        )
        
        # Add headers for CORS and file handling
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 200MB.'}), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    return jsonify({'error': 'Internal server error occurred.'}), 500


def cleanup_old_jobs():
    """Cleanup old job results to prevent memory leaks."""
    current_time = time.time()
    max_age = 3600  # 1 hour
    
    expired_jobs = []
    for job_id, result in job_results.items():
        if current_time - result.get('end_time', current_time) > max_age:
            expired_jobs.append(job_id)
            # Also cleanup output files
            if 'result' in result and 'output_path' in result['result']:
                output_path = result['result']['output_path']
                if output_path and os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except:
                        pass
    
    for job_id in expired_jobs:
        del job_results[job_id]
    
    if expired_jobs:
        logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")


if __name__ == '__main__':
    # Get configuration from environment
    port = int(os.environ.get('PORT', 9001))  # Changed default port to 9001
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    print("🎬 AI Profanity Filter Backend Server Starting...")
    print(f"🐍 Python Version: {sys.version}")
    print(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"🔗 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📁 Processed folder: {os.path.abspath(PROCESSED_FOLDER)}")
    print(f"🎯 Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"🔧 Supported modes: {', '.join([m['mode'] for m in get_supported_modes()])}")
    print(f"🚀 Server running on http://{host}:{port}")
    
    # Setup periodic cleanup (in production, use a proper task scheduler)
    import atexit
    import signal
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down server...")
        cleanup_old_jobs()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
