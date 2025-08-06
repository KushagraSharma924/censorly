"""
Modern API Routes for Abuse Classification
Refactored to use the new abuse classifier instead of legacy rule-based detection.
"""

import os
import uuid
import json
import shutil
import pathlib
from datetime import datetime, timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from marshmallow import Schema, fields, ValidationError, validate

from models.saas_models import db, User, Job, TrainingSession
from api.auth import api_key_required
from services.abuse_classifier import load_classifier, get_classifier_info
from utils.ffmpeg_tools import get_video_duration
from config import Config

# Import celery task with fallback
try:
    from services.celery_worker import process_video_task
    CELERY_AVAILABLE = True
except (ImportError, AttributeError):
    CELERY_AVAILABLE = False

# Create a dummy task class for when Celery is not available
class DummyTask:
    def apply_async(self, *args, **kwargs):
        # Return a dummy result that mimics Celery task
        class DummyResult:
            def __init__(self):
                import uuid
                self.id = str(uuid.uuid4())
        return DummyResult()

# Use dummy task if Celery is not available
if not CELERY_AVAILABLE:
    process_video_task = DummyTask()

# Create blueprint
api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Validation schemas
class VideoUploadSchema(Schema):
    censoring_mode = fields.Str(validate=validate.OneOf(['beep', 'mute', 'cut-scene', 'cut-nsfw']), missing='beep')
    abuse_threshold = fields.Float(validate=validate.Range(min=0.1, max=1.0), missing=0.3)
    languages = fields.List(fields.Str(), missing=['auto'])
    whisper_model = fields.Str(validate=validate.OneOf(['tiny', 'base', 'small', 'medium', 'large']), missing='base')


class AbuseTestSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    return_confidence = fields.Bool(missing=True)


def allowed_file(filename, allowed_extensions):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_current_user(use_api_key=False):
    """Get current user from JWT or API key."""
    if use_api_key and hasattr(request, 'current_user'):
        return request.current_user
    
    try:
        user_id = get_jwt_identity()
        if user_id is None:
            return None
        
        # User ID is a UUID string, not an integer
        user = User.query.get(user_id)
        return user
    except Exception as e:
        current_app.logger.error(f"Error getting current user: {e}, user_id: {get_jwt_identity()}")
        return None


def get_whisper_model_for_tier(subscription_tier):
    """
    Determine the appropriate Whisper model based on subscription tier.
    
    Args:
        subscription_tier (str): User's subscription tier
        
    Returns:
        str: Whisper model name ('base', 'medium', or 'large')
    """
    tier_to_model = {
        'free': 'base',
        'basic': 'medium', 
        'pro': 'large',
        'enterprise': 'large'
    }
    
    return tier_to_model.get(subscription_tier, 'base')


@api_v2_bp.route('/classifier-info', methods=['GET'])
@api_key_required
def classifier_info():
    """
    Get information about the currently loaded classifier.
    """
    try:
        info = get_classifier_info()
        return jsonify({
            'classifier_info': info,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v2_bp.route('/process-video', methods=['POST'])
@jwt_required()
def upload_and_process_video():
    """
    Upload and process video with modern abuse classification.
    """
    try:
        # Debug: Log JWT identity
        user_id = get_jwt_identity()
        current_app.logger.info(f"JWT identity: {user_id}, type: {type(user_id)}")
        
        user = get_current_user()
        if not user:
            current_app.logger.error(f"User not found for JWT identity: {user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        current_app.logger.info(f"User found: {user.email}, ID: {user.id}")
        
        # Check if file was uploaded
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Debug: Check file size before processing
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        current_app.logger.info(f"Uploaded file size: {file_size} bytes")
        
        if file_size == 0:
            return jsonify({'error': 'Uploaded file is empty'}), 400
        
        # Validate file type
        allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'}
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Parse and validate form data
        try:
            form_data = {
                'censoring_mode': request.form.get('censoring_mode', 'beep'),
                'abuse_threshold': float(request.form.get('abuse_threshold', 0.3)),
                'languages': request.form.get('languages', 'auto').split(','),
                'whisper_model': 'base'  # Will be overridden by subscription tier
            }
            
            schema = VideoUploadSchema()
            validated_data = schema.load(form_data)
            
            # Override whisper model based on user's subscription tier
            subscription_whisper_model = get_whisper_model_for_tier(user.subscription_tier)
            validated_data['whisper_model'] = subscription_whisper_model
            current_app.logger.info(f"User tier: {user.subscription_tier}, Using Whisper model: {subscription_whisper_model}")
            
        except (ValueError, ValidationError) as e:
            return jsonify({'error': f'Invalid form data: {str(e)}'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        stored_filename = f"{file_id}.{file_extension}"
        
        upload_dir = pathlib.Path(current_app.config['UPLOAD_FOLDER']) / str(user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / stored_filename
        
        current_app.logger.info(f"Saving file to: {file_path}")
        file.save(str(file_path))
        
        # Verify file was saved correctly
        saved_file_size = file_path.stat().st_size
        current_app.logger.info(f"File saved successfully. Size: {saved_file_size} bytes")
        
        if saved_file_size == 0:
            current_app.logger.error("File was saved but is empty!")
            return jsonify({'error': 'File upload failed - saved file is empty'}), 400
        
        # Get video duration for estimation
        try:
            duration = get_video_duration(str(file_path))
        except:
            duration = 0
        
        # Create job record
        job = Job(
            user_id=user.id,
            original_filename=filename,
            file_size=file.content_length or 0,
            duration=duration,
            status='pending',
            censoring_mode=validated_data['censoring_mode'],
            profanity_threshold=validated_data['abuse_threshold'],
            languages=json.dumps(validated_data['languages']),
            input_path=str(file_path),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start background processing 
        if CELERY_AVAILABLE:
            try:
                task = process_video_task.apply_async(
                    args=[job.id, job.input_path, job.censoring_mode],
                    kwargs={
                        'abuse_threshold': validated_data['abuse_threshold'],
                        'whisper_model': validated_data['whisper_model']
                    }
                )
                
                # Update job with task ID
                job.celery_task_id = task.id
                task_id = task.id
            except Exception as e:
                current_app.logger.error(f"Failed to start Celery task: {e}")
                # Fallback to dummy task
                task = process_video_task.apply_async()
                job.celery_task_id = task.id
                task_id = task.id
        else:
            # Fallback: use dummy task to get consistent behavior
            task = process_video_task.apply_async()
            job.celery_task_id = task.id
            task_id = task.id
            current_app.logger.info(f"Celery not available, using mock task ID: {task_id}")
            
            # For development: immediately process small files
            try:
                file_size_mb = job.file_size / (1024 * 1024) if job.file_size else 0
                if file_size_mb < 50:  # Process files smaller than 50MB immediately
                    current_app.logger.info(f"Processing small file immediately: {job.original_filename}")
                    
                    # Import and use the actual video processor
                    from video_processor_v2 import process_video
                    import time
                    
                    start_time = time.time()
                    
                    # Set up output directory
                    output_dir = pathlib.Path(job.input_path).parent / "processed"
                    output_dir.mkdir(exist_ok=True)
                    
                    # Process the video with the actual AI model
                    current_app.logger.info(f"Starting real video processing for {job.original_filename}")
                    current_app.logger.info(f"Video file path: {job.input_path}")
                    
                    # Ensure we have an absolute path
                    video_path = job.input_path
                    if not os.path.isabs(video_path):
                        video_path = os.path.abspath(video_path)
                        current_app.logger.info(f"Converted to absolute path: {video_path}")
                    
                    processing_result = process_video(
                        input_path=video_path,
                        mode=job.censoring_mode,
                        temp_dir=str(output_dir)
                    )
                    
                    processing_time = time.time() - start_time
                    
                    # Update job with real results
                    if processing_result.get('output_path'):
                        job.status = 'completed'
                        job.completed_at = datetime.utcnow()
                        job.output_path = processing_result['output_path']
                        job.processing_time = processing_time
                        job.profane_segments_count = len(processing_result.get('abusive_segments', []))
                        job.download_url = f"/api/download/{job.id}"
                        current_app.logger.info(f"Real video processing completed for job {job.id}")
                        current_app.logger.info(f"Found {job.profane_segments_count} abusive segments")
                    else:
                        job.status = 'failed'
                        job.error_message = "Video processing failed - no output generated"
                        current_app.logger.error(f"Video processing failed for job {job.id}")
                    
            except Exception as e:
                current_app.logger.error(f"Video processing failed: {e}")
                job.status = 'failed'
                job.error_message = str(e)
                
        db.session.commit()
        
        return jsonify({
            'job_id': job.id,
            'task_id': task_id,
            'status': 'queued',
            'estimated_duration': max(30, (job.duration or 0) * 2),  # Calculate estimated duration
            'parameters': validated_data,
            'message': 'Video uploaded successfully and processing started',
            'processor_version': '2.0',
            'celery_available': CELERY_AVAILABLE
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v2_bp.route('/job/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """
    Get the status of a processing job.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        job = Job.query.filter_by(id=job_id, user_id=user.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Build response with available job data (no results field in model)
        response = {
            'job_id': job.id,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'updated_at': job.created_at.isoformat() if job.created_at else None,  # Use created_at as fallback
            'input_filename': job.original_filename,  # Use correct field name
            'progress': job.progress or 0,
            'estimated_duration': max(30, (job.duration or 0) * 2),  # Calculate estimated duration
            'processor_version': '2.0'
        }
        
        # Add results if completed
        if job.status == 'completed':
            response.update({
                'results': {
                    'duration': job.duration,
                    'profane_segments_count': job.profane_segments_count or 0,
                    'download_url': job.download_url,
                    'processing_time': job.processing_time
                },
                'download_url': job.download_url,
                'duration': job.duration or 0,
                'output_available': bool(job.download_url)
            })
        
        # Add error info if failed
        if job.status == 'failed':
            response['error'] = job.error_message or 'Unknown error'
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v2_bp.route('/job/<int:job_id>/download', methods=['GET'])
@jwt_required()
def download_processed_video(job_id):
    """
    Download the processed video file.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        job = Job.query.filter_by(id=job_id, user_id=user.id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.status != 'completed':
            return jsonify({'error': 'Job not completed yet'}), 400
        
        # Get output path from results
        if not job.results:
            return jsonify({'error': 'No results available'}), 404
        
        try:
            results = json.loads(job.results)
            output_path = results.get('output_path')
        except:
            return jsonify({'error': 'Could not parse job results'}), 500
        
        if not output_path or not os.path.exists(output_path):
            return jsonify({'error': 'Processed video file not found'}), 404
        
        # Determine download filename
        original_name = pathlib.Path(job.input_filename).stem
        mode = json.loads(job.parameters).get('censoring_mode', 'processed')
        file_extension = pathlib.Path(output_path).suffix
        download_name = f"{original_name}_{mode}{file_extension}"
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v2_bp.route('/jobs', methods=['GET'])
@jwt_required()
def list_user_jobs():
    """
    List all jobs for the current user.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Filter parameters
        status_filter = request.args.get('status')
        
        # Build query
        query = Job.query.filter_by(user_id=user.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        query = query.order_by(Job.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        jobs = []
        for job in pagination.items:
            job_data = {
                'job_id': job.id,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'updated_at': job.created_at.isoformat() if job.created_at else None,  # Job model doesn't have updated_at
                'input_filename': job.original_filename,
                'job_type': 'video_processing',  # Static value since model doesn't have this field
                'progress': job.progress or 0
            }
            
            # Add summary results if completed
            if job.status == 'completed':
                job_data['summary'] = {
                    'duration': job.duration or 0,
                    'abusive_segments_count': job.profane_segments_count or 0,
                    'output_available': bool(job.download_url)
                }
            
            jobs.append(job_data)
        
        return jsonify({
            'jobs': jobs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'processor_version': '2.0'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v2_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the v2 API.
    """
    try:
        # Check classifier status
        classifier_status = "unknown"
        try:
            info = get_classifier_info()
            classifier_status = "loaded" if info.get('is_loaded') else "not_loaded"
        except:
            classifier_status = "error"
        
        return jsonify({
            'status': 'healthy',
            'version': '2.0',
            'timestamp': datetime.utcnow().isoformat(),
            'classifier_status': classifier_status,
            'features': [
                'modern_abuse_classification',
                'multilingual_support',
                'confidence_scoring',
                'video_processing',
                'job_management'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'version': '2.0'
        }), 500


# Error handlers
@api_v2_bp.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413


@api_v2_bp.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400


@api_v2_bp.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# V2 Hybrid Detector Endpoints

@api_v2_bp.route('/detect-text', methods=['POST'])
@jwt_required()
def detect_text_abuse():
    """Direct text abuse detection endpoint using hybrid detector"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        if not text or not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Initialize hybrid detector
        try:
            from services.hybrid_detector import HybridAbuseDetector
            model_path = os.getenv('TRANSFORMER_MODEL_PATH')
            
            if model_path and os.path.exists(model_path):
                detector = HybridAbuseDetector(
                    transformer_model_path=model_path,
                    use_transformer=True,
                    transformer_threshold=0.75,
                    ensemble_mode="hybrid"
                )
            else:
                detector = HybridAbuseDetector(
                    use_transformer=False,
                    ensemble_mode="keyword_first"
                )
        except Exception as e:
            current_app.logger.error(f"Failed to initialize hybrid detector: {e}")
            return jsonify({'error': 'Detector initialization failed'}), 500
        
        # Get detection result
        result = detector.predict(text, return_score=True)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'api_version': 'v2'
        })
        
    except Exception as e:
        current_app.logger.error(f"Text detection error: {e}")
        return jsonify({'error': f'Detection failed: {str(e)}'}), 500


@api_v2_bp.route('/detect-batch', methods=['POST'])
@jwt_required()
def detect_batch_text():
    """Batch text abuse detection endpoint"""
    try:
        data = request.get_json()
        if not data or 'texts' not in data:
            return jsonify({'error': 'Texts array is required'}), 400
        
        texts = data['texts']
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({'error': 'Texts must be a non-empty array'}), 400
        
        if len(texts) > 100:  # Limit batch size
            return jsonify({'error': 'Maximum 100 texts per batch'}), 400
        
        # Initialize hybrid detector
        try:
            from services.hybrid_detector import HybridAbuseDetector
            model_path = os.getenv('TRANSFORMER_MODEL_PATH')
            
            if model_path and os.path.exists(model_path):
                detector = HybridAbuseDetector(
                    transformer_model_path=model_path,
                    use_transformer=True,
                    transformer_threshold=0.75,
                    ensemble_mode="hybrid"
                )
            else:
                detector = HybridAbuseDetector(
                    use_transformer=False,
                    ensemble_mode="keyword_first"
                )
        except Exception as e:
            current_app.logger.error(f"Failed to initialize hybrid detector: {e}")
            return jsonify({'error': 'Detector initialization failed'}), 500
        
        # Process batch
        results = detector.predict_batch(texts)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results),
            'api_version': 'v2'
        })
        
    except Exception as e:
        current_app.logger.error(f"Batch detection error: {e}")
        return jsonify({'error': f'Batch detection failed: {str(e)}'}), 500


@api_v2_bp.route('/model-info', methods=['GET'])
@jwt_required()
def get_model_info():
    """Get information about the current abuse detection model"""
    try:
        from services.hybrid_detector import HybridAbuseDetector
        model_path = os.getenv('TRANSFORMER_MODEL_PATH')
        
        if model_path and os.path.exists(model_path):
            detector = HybridAbuseDetector(
                transformer_model_path=model_path,
                use_transformer=True,
                transformer_threshold=0.75,
                ensemble_mode="hybrid"
            )
        else:
            detector = HybridAbuseDetector(
                use_transformer=False,
                ensemble_mode="keyword_first"
            )
        
        model_info = detector.get_model_info()
        stats = detector.get_stats()
        
        return jsonify({
            'status': 'success',
            'model_info': model_info,
            'stats': stats,
            'api_version': 'v2'
        })
        
    except Exception as e:
        current_app.logger.error(f"Model info error: {e}")
        return jsonify({'error': f'Failed to get model info: {str(e)}'}), 500


@api_v2_bp.route('/benchmark', methods=['POST'])
@jwt_required()
def benchmark_detector():
    """Benchmark the abuse detector with test texts"""
    try:
        data = request.get_json() or {}
        test_texts = data.get('test_texts', [
            "This is a normal sentence.",
            "This is fucking terrible!",
            "You are so stupid and annoying.",
            "Great work on this project!",
            "Tu chutiya hai yaar",
            "Bahut accha kaam kiya hai"
        ])
        
        if len(test_texts) > 50:  # Limit for benchmarking
            return jsonify({'error': 'Maximum 50 texts for benchmarking'}), 400
        
        from services.hybrid_detector import HybridAbuseDetector
        model_path = os.getenv('TRANSFORMER_MODEL_PATH')
        
        if model_path and os.path.exists(model_path):
            detector = HybridAbuseDetector(
                transformer_model_path=model_path,
                use_transformer=True,
                transformer_threshold=0.75,
                ensemble_mode="hybrid"
            )
        else:
            detector = HybridAbuseDetector(
                use_transformer=False,
                ensemble_mode="keyword_first"
            )
        
        # Run benchmark
        import time
        start_time = time.time()
        
        results = []
        for text in test_texts:
            result = detector.predict(text, return_score=True)
            results.append(result)
        
        total_time = time.time() - start_time
        avg_time = (total_time / len(test_texts)) * 1000  # Convert to ms
        
        stats = detector.get_stats()
        
        return jsonify({
            'status': 'success',
            'benchmark_results': results,
            'performance': {
                'total_time_ms': total_time * 1000,
                'avg_time_per_text_ms': avg_time,
                'texts_processed': len(test_texts)
            },
            'detector_stats': stats,
            'api_version': 'v2'
        })
        
    except Exception as e:
        current_app.logger.error(f"Benchmark error: {e}")
        return jsonify({'error': f'Benchmark failed: {str(e)}'}), 500


@api_v2_bp.route('/health-detector', methods=['GET'])
def health_check_detector():
    """Health check for v2 API with model status"""
    try:
        from services.hybrid_detector import HybridAbuseDetector
        
        # Try to initialize detector
        model_path = os.getenv('TRANSFORMER_MODEL_PATH')
        detector_status = "keyword_only"
        
        try:
            if model_path and os.path.exists(model_path):
                detector = HybridAbuseDetector(
                    transformer_model_path=model_path,
                    use_transformer=True,
                    transformer_threshold=0.75,
                    ensemble_mode="hybrid"
                )
                detector_status = "transformer_hybrid"
            else:
                detector = HybridAbuseDetector(
                    use_transformer=False,
                    ensemble_mode="keyword_first"
                )
            
            # Test with a simple prediction
            test_result = detector.predict("test", return_score=False)
            model_working = test_result is not None
            
        except Exception as e:
            current_app.logger.error(f"Health check detector error: {e}")
            model_working = False
        
        return jsonify({
            'status': 'healthy',
            'api_version': 'v2',
            'detector_status': detector_status,
            'model_working': model_working,
            'transformer_model_path': model_path if model_path else None,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'api_version': 'v2',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
