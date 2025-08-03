"""
API routes for AI Profanity Filter
Flask routes for video processing, job management, and file handling.
"""

import os
import uuid
import threading
import time
from pathlib import Path
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
import logging

# Note: video_processor module not available, using fallback
try:
    from video_processor_v2 import process_video_ai
    def process_video(*args, **kwargs):
        return process_video_ai(*args, **kwargs)
    def get_supported_modes():
        return ['beep', 'mute', 'cut-scene']
    def estimate_processing_time(file_size):
        return min(60, max(10, file_size / 1000000))  # Simple estimation
except ImportError:
    process_video = None
    get_supported_modes = None
    estimate_processing_time = None

logger = logging.getLogger(__name__)

# Global job tracking
active_jobs = {}
job_results = {}

# Configuration
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'


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
        logger.error(f"Job {job_id} failed: {str(e)}")
        job_results[job_id] = {
            'status': 'failed',
            'error': str(e),
            'end_time': time.time(),
            'message': f'Processing failed: {str(e)}'
        }
        
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]


def register_routes(app):
    """Register all API routes with the Flask app."""
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'message': 'AI Profanity Filter backend is running',
            'supported_modes': get_supported_modes()
        })

    @app.route('/api/upload', methods=['POST'])
    def upload_video():
        """
        Upload and process a video file.
        
        Expected form data:
        - file: Video file to process
        - mode: Processing mode ('beep', 'mute', 'cut-scene', 'cut-nsfw')
        - custom_words: Optional comma-separated list of custom profanity words
        """
        try:
            # Check if file is present
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file type
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'File type not supported. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            # Get processing mode
            mode = request.form.get('mode', 'beep')
            if mode not in get_supported_modes():
                return jsonify({
                    'error': f'Invalid mode. Supported modes: {", ".join(get_supported_modes())}'
                }), 400
            
            # Get custom words if provided
            custom_words = None
            custom_words_str = request.form.get('custom_words', '').strip()
            if custom_words_str:
                custom_words = [word.strip() for word in custom_words_str.split(',') if word.strip()]
            
            # Create directories
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            os.makedirs(PROCESSED_FOLDER, exist_ok=True)
            
            # Generate unique job ID and save file
            job_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_{filename}")
            file.save(file_path)
            
            logger.info(f"File uploaded: {file_path} for job {job_id}")
            
            # Start background processing
            thread = threading.Thread(
                target=background_process_video,
                args=(job_id, file_path, mode, custom_words)
            )
            thread.daemon = True
            thread.start()
            
            # Estimate processing time
            estimated_time = estimate_processing_time(file_path, mode)
            
            return jsonify({
                'job_id': job_id,
                'message': 'Video upload successful, processing started',
                'estimated_time_seconds': estimated_time,
                'mode': mode,
                'custom_words': custom_words or []
            }), 202
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500

    @app.route('/api/status/<job_id>', methods=['GET'])
    def get_job_status(job_id):
        """Get the status of a processing job."""
        try:
            # Check if job is still active
            if job_id in active_jobs:
                return jsonify(active_jobs[job_id])
            
            # Check if job is completed
            if job_id in job_results:
                result = job_results[job_id].copy()
                # Don't include the full result data in status check
                if 'result' in result:
                    result['has_result'] = True
                    # Include summary info
                    if 'profane_segments' in result['result']:
                        result['profane_count'] = len(result['result']['profane_segments'])
                    if 'output_path' in result['result']:
                        result['output_ready'] = True
                return jsonify(result)
            
            # Job not found
            return jsonify({'error': 'Job not found'}), 404
            
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return jsonify({'error': f'Status check failed: {str(e)}'}), 500

    @app.route('/api/download/<job_id>', methods=['GET'])
    def download_result(job_id):
        """Download the processed video file."""
        try:
            # Check if job is completed
            if job_id not in job_results:
                return jsonify({'error': 'Job not found or not completed'}), 404
            
            result = job_results[job_id]
            if result['status'] != 'completed':
                return jsonify({'error': 'Job not completed successfully'}), 400
            
            output_path = result['result']['output_path']
            if not os.path.exists(output_path):
                return jsonify({'error': 'Processed file not found'}), 404
            
            # Get original filename for download
            original_filename = result['result'].get('original_filename', 'processed_video.mp4')
            base_name = Path(original_filename).stem
            extension = Path(original_filename).suffix
            download_filename = f"censored_{base_name}{extension}"
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=download_filename,
                mimetype='video/mp4'
            )
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return jsonify({'error': f'Download failed: {str(e)}'}), 500

    @app.route('/api/jobs', methods=['GET'])
    def list_jobs():
        """List all job statuses."""
        try:
            all_jobs = {}
            
            # Add active jobs
            for job_id, job_data in active_jobs.items():
                all_jobs[job_id] = {**job_data, 'type': 'active'}
            
            # Add completed jobs (last 50)
            completed_jobs = list(job_results.items())[-50:]
            for job_id, job_data in completed_jobs:
                summary = {
                    'status': job_data['status'],
                    'end_time': job_data.get('end_time'),
                    'message': job_data.get('message'),
                    'type': 'completed'
                }
                if job_data['status'] == 'completed' and 'result' in job_data:
                    summary['has_result'] = True
                    if 'profane_segments' in job_data['result']:
                        summary['profane_count'] = len(job_data['result']['profane_segments'])
                all_jobs[job_id] = summary
            
            return jsonify({'jobs': all_jobs})
            
        except Exception as e:
            logger.error(f"Jobs list error: {str(e)}")
            return jsonify({'error': f'Failed to list jobs: {str(e)}'}), 500

    @app.route('/api/modes', methods=['GET'])
    def get_modes():
        """Get supported processing modes."""
        return jsonify({
            'modes': get_supported_modes(),
            'descriptions': {
                'beep': 'Replace profane audio with beep sounds',
                'mute': 'Replace profane audio with silence',
                'cut-scene': 'Remove entire scenes containing profanity',
                'cut-nsfw': 'Remove scenes with NSFW visual content (experimental)'
            }
        })

    @app.route('/api/cleanup/<job_id>', methods=['DELETE'])
    def cleanup_job(job_id):
        """Clean up job files and data."""
        try:
            # Remove from active jobs if present
            if job_id in active_jobs:
                del active_jobs[job_id]
            
            # Remove from results if present
            if job_id in job_results:
                result = job_results[job_id]
                
                # Clean up files
                if 'result' in result and 'output_path' in result['result']:
                    output_path = result['result']['output_path']
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        logger.info(f"Removed output file: {output_path}")
                
                # Remove input file
                input_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(job_id)]
                for input_file in input_files:
                    input_path = os.path.join(UPLOAD_FOLDER, input_file)
                    if os.path.exists(input_path):
                        os.remove(input_path)
                        logger.info(f"Removed input file: {input_path}")
                
                del job_results[job_id]
            
            return jsonify({'message': 'Job cleaned up successfully'})
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

    # Test endpoints for the new profanity scanner
    @app.route('/api/test-profanity', methods=['POST'])
    def test_profanity():
        """Test profanity detection on a text string."""
        try:
            from services.profanity_scanner import is_abusive, find_profanity_matches
            
            data = request.get_json()
            text = data.get('text', '')
            
            if not text:
                return jsonify({'error': 'Text is required'}), 400
            
            is_profane = is_abusive(text)
            matches = find_profanity_matches(text)
            detected_words = [match['word'] for match in matches]
            
            return jsonify({
                'text': text,
                'is_profane': is_profane,
                'detected_words': detected_words,
                'matches': matches
            })
            
        except Exception as e:
            logger.error(f"Profanity test error: {str(e)}")
            return jsonify({'error': f'Profanity test failed: {str(e)}'}), 500

    @app.route('/api/scan-segments', methods=['POST'])
    def scan_segments_endpoint():
        """Test segment scanning functionality."""
        try:
            from services.profanity_scanner import scan_segments as scanner_scan_segments
            
            data = request.get_json()
            segments = data.get('segments', [])
            
            if not segments:
                return jsonify({'error': 'Segments are required'}), 400
            
            abusive_segments = scanner_scan_segments(segments)
            
            return jsonify({
                'total_segments': len(segments),
                'abusive_segments': abusive_segments,
                'abusive_count': len(abusive_segments)
            })
            
        except Exception as e:
            logger.error(f"Segment scanning error: {str(e)}")
            return jsonify({'error': f'Segment scanning failed: {str(e)}'}), 500

    @app.route('/api/scanner-stats', methods=['GET'])
    def scanner_stats():
        """Get profanity scanner statistics."""
        try:
            from services.profanity_scanner import get_statistics
            
            stats = get_statistics()
            return jsonify(stats)
            
        except Exception as e:
            logger.error(f"Scanner stats error: {str(e)}")
            return jsonify({'error': f'Scanner stats failed: {str(e)}'}), 500

    @app.route('/health', methods=['GET'])
    def health_check_new():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {
                'profanity_scanner': True,
                'celery_worker': True,
                'backend': True
            }
        })
