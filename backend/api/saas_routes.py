"""
SaaS API routes for AI Profanity Filter Platform
Multi-user authenticated routes for video processing, training, and job management.
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from marshmallow import Schema, fields, ValidationError, validate

from models.saas_models import db, User, Job, TrainingSession
from api.auth import api_key_required
# Import Celery tasks with fallback
try:
    from services.celery_worker import process_video_task, train_dataset_task
    CELERY_TASKS_AVAILABLE = True
except ImportError:
    CELERY_TASKS_AVAILABLE = False
    # Create dummy tasks for when Celery is not available
    class DummyTask:
        def apply_async(self, *args, **kwargs):
            return type('DummyResult', (), {
                'id': 'mock_task_id', 
                'ready': lambda: False,
                'state': 'PENDING'
            })()
        
        def delay(self, *args, **kwargs):
            return self.apply_async(*args, **kwargs)
    
    process_video_task = DummyTask()
    train_dataset_task = DummyTask()
from utils.audio_utils import get_audio_duration
from config import Config

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Validation schemas
class VideoUploadSchema(Schema):
    censoring_mode = fields.Str(validate=validate.OneOf(['beep', 'mute', 'cut']), missing='beep')
    profanity_threshold = fields.Float(validate=validate.Range(min=0.1, max=1.0), missing=0.8)
    languages = fields.List(fields.Str(), missing=['auto'])
    whisper_model = fields.Str(validate=validate.OneOf(['tiny', 'base', 'small', 'medium', 'large']), missing='base')


class TrainingUploadSchema(Schema):
    description = fields.Str(validate=validate.Length(max=255))


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
        return User.query.get(int(user_id))
    except:
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


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Profanity Filter SaaS backend is running',
        'version': '2.0.0',
        'features': ['multi-user', 'background-processing', 'custom-training']
    })


@api_bp.route('/upload', methods=['GET', 'POST', 'OPTIONS'])
@jwt_required(optional=True)
def upload_video():
    """
    Upload and process a video file.
    Requires JWT token authentication.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Upload endpoint available'}), 200
    
    # Handle GET request with helpful error message
    if request.method == 'GET':
        return jsonify({
            'error': 'GET method not supported for uploads',
            'message': 'Please use POST method to upload files',
            'supported_methods': ['POST'],
            'endpoint': '/api/upload'
        }), 405
    
    # For POST requests, require JWT authentication
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Validate form data
        schema = VideoUploadSchema()
        try:
            form_dict = request.form.to_dict()
            # Parse languages JSON string if present
            if 'languages' in form_dict:
                try:
                    form_dict['languages'] = json.loads(form_dict['languages'])
                except (json.JSONDecodeError, TypeError):
                    form_dict['languages'] = ['auto']  # fallback
            
            form_data = schema.load(form_dict)
            
            # Override whisper model based on user's subscription tier
            subscription_whisper_model = get_whisper_model_for_tier(user.subscription_tier)
            form_data['whisper_model'] = subscription_whisper_model
            current_app.logger.info(f"User tier: {user.subscription_tier}, Using Whisper model: {subscription_whisper_model}")
            
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({
                'error': f'File type not supported. Allowed types: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
            }), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > current_app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large'}), 413
        
        # Create user directories
        user_upload_dir = Config.get_user_upload_folder(user.id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique job ID and save file
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = user_upload_dir / f"{job_id}_{filename}"
        file.save(str(file_path))
        
        # Get video duration for plan validation
        try:
            duration = get_audio_duration(str(file_path))
            duration_minutes = duration / 60 if duration else 0
        except:
            duration = None
            duration_minutes = 0
        
        # Check user plan limits
        if not user.can_process_video(duration_minutes):
            file_path.unlink()  # Remove uploaded file
            limits = user.get_plan_limits()
            return jsonify({
                'error': f'Video too long for your plan. Maximum: {limits["max_video_minutes"]} minutes'
            }), 403
        
        # Create job record
        job = Job(
            id=job_id,
            user_id=user.id,
            original_filename=filename,
            file_size=file_size,
            duration=duration,
            censoring_mode=form_data['censoring_mode'],
            profanity_threshold=form_data['profanity_threshold'],
            languages=json.dumps(form_data['languages']),
            input_path=str(file_path),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start background processing
        task = process_video_task.delay(
            job_id=job_id,
            user_id=user.id,
            input_file_path=str(file_path),
            config_options=form_data
        )
        
        # Update job with Celery task ID
        job.celery_task_id = task.id
        db.session.commit()
        
        current_app.logger.info(f"Video upload started for user {user.id}, job {job_id}")
        
        return jsonify({
            'job_id': job_id,
            'message': 'Video upload successful, processing started',
            'status': 'pending',
            'estimated_time_minutes': max(duration_minutes * 2, 2) if duration_minutes else 5,
            'config': form_data
        }), 202
        
    except Exception as e:
        current_app.logger.error(f"Upload error for user {user.id}: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@api_bp.route('/train', methods=['POST'])
@jwt_required()
def upload_training_data():
    """
    Upload CSV file to train custom profanity dataset.
    Requires JWT token authentication.
    """
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Validate form data
        schema = TrainingUploadSchema()
        try:
            form_data = schema.load(request.form.to_dict())
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No CSV file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type (CSV only)
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed for training'}), 400
        
        # Create user directories
        user_upload_dir = Config.get_user_upload_folder(user.id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique training session ID and save file
        training_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = user_upload_dir / f"training_{training_id}_{filename}"
        file.save(str(file_path))
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Create training session record
        session = TrainingSession(
            id=training_id,
            user_id=user.id,
            original_filename=filename,
            file_size=file_size
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Start background training
        task = train_dataset_task.delay(
            training_session_id=training_id,
            user_id=user.id,
            csv_file_path=str(file_path)
        )
        
        # Update session with Celery task ID
        session.celery_task_id = task.id
        db.session.commit()
        
        current_app.logger.info(f"Training started for user {user.id}, session {training_id}")
        
        return jsonify({
            'training_session_id': training_id,
            'message': 'Training data uploaded successfully, training started',
            'status': 'pending'
        }), 202
        
    except Exception as e:
        current_app.logger.error(f"Training upload error for user {user.id}: {str(e)}")
        return jsonify({'error': f'Training upload failed: {str(e)}'}), 500


@api_bp.route('/jobs', methods=['GET'])
@jwt_required()
def list_user_jobs():
    """List all jobs for the authenticated user."""
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status_filter = request.args.get('status')
        
        # Build query
        query = Job.query.filter_by(user_id=user.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Order by creation date (newest first)
        query = query.order_by(Job.created_at.desc())
        
        # Paginate
        jobs_paginated = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Convert to dict
        jobs_data = [job.to_dict() for job in jobs_paginated.items]
        
        return jsonify({
            'jobs': jobs_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': jobs_paginated.total,
                'pages': jobs_paginated.pages,
                'has_next': jobs_paginated.has_next,
                'has_prev': jobs_paginated.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Jobs list error for user {user.id}: {str(e)}")
        return jsonify({'error': f'Failed to list jobs: {str(e)}'}), 500


@api_bp.route('/jobs/<job_id>', methods=['GET'])
@jwt_required()
def get_job_status(job_id):
    """Get detailed status of a specific job."""
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Find job belonging to user
        job = Job.query.filter_by(id=job_id, user_id=user.id).first()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get Celery task status if available
        if job.celery_task_id and job.status == 'processing':
            from services.celery_worker import celery
            task = celery.AsyncResult(job.celery_task_id)
            
            if task.state == 'PROGRESS':
                task_info = task.info or {}
                job.progress = task_info.get('progress', job.progress)
                db.session.commit()
        
        return jsonify(job.to_dict())
        
    except Exception as e:
        current_app.logger.error(f"Job status error for user {user.id}, job {job_id}: {str(e)}")
        return jsonify({'error': f'Failed to get job status: {str(e)}'}), 500


@api_bp.route('/download/<job_id>', methods=['GET'])
@jwt_required()
def download_processed_video(job_id):
    """Download the processed video file."""
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Find completed job belonging to user
        job = Job.query.filter_by(id=job_id, user_id=user.id).first()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.status != 'completed':
            return jsonify({'error': 'Job not completed successfully'}), 400
        
        if not job.output_path or not Path(job.output_path).exists():
            return jsonify({'error': 'Processed file not found or expired'}), 404
        
        # Generate download filename
        base_name = Path(job.original_filename).stem
        extension = Path(job.original_filename).suffix
        download_filename = f"censored_{base_name}{extension}"
        
        return send_file(
            job.output_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        current_app.logger.error(f"Download error for user {user.id}, job {job_id}: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@api_bp.route('/training', methods=['GET'])
@jwt_required()
def list_training_sessions():
    """List all training sessions for the authenticated user."""
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get training sessions
        sessions_paginated = TrainingSession.query.filter_by(user_id=user.id)\
            .order_by(TrainingSession.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Convert to dict
        sessions_data = [session.to_dict() for session in sessions_paginated.items]
        
        return jsonify({
            'training_sessions': sessions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': sessions_paginated.total,
                'pages': sessions_paginated.pages,
                'has_next': sessions_paginated.has_next,
                'has_prev': sessions_paginated.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Training sessions list error for user {user.id}: {str(e)}")
        return jsonify({'error': f'Failed to list training sessions: {str(e)}'}), 500


@api_bp.route('/training/<training_id>', methods=['GET'])
@jwt_required()
def get_training_status(training_id):
    """Get detailed status of a specific training session."""
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Find training session belonging to user
        session = TrainingSession.query.filter_by(id=training_id, user_id=user.id).first()
        
        if not session:
            return jsonify({'error': 'Training session not found'}), 404
        
        return jsonify(session.to_dict())
        
    except Exception as e:
        current_app.logger.error(f"Training status error for user {user.id}, session {training_id}: {str(e)}")
        return jsonify({'error': f'Failed to get training status: {str(e)}'}), 500


@api_bp.route('/stats', methods=['GET'])
@jwt_required(optional=True)
@api_key_required
def get_user_stats():
    """Get user statistics and usage information."""
    user = get_current_user(use_api_key=True)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Count jobs by status
        total_jobs = Job.query.filter_by(user_id=user.id).count()
        completed_jobs = Job.query.filter_by(user_id=user.id, status='completed').count()
        failed_jobs = Job.query.filter_by(user_id=user.id, status='failed').count()
        pending_jobs = Job.query.filter_by(user_id=user.id, status='pending').count()
        processing_jobs = Job.query.filter_by(user_id=user.id, status='processing').count()
        
        # Count training sessions
        total_training = TrainingSession.query.filter_by(user_id=user.id).count()
        completed_training = TrainingSession.query.filter_by(user_id=user.id, status='completed').count()
        
        # Get plan limits
        limits = user.get_plan_limits()
        
        return jsonify({
            'user': user.to_dict(),
            'job_stats': {
                'total': total_jobs,
                'completed': completed_jobs,
                'failed': failed_jobs,
                'pending': pending_jobs,
                'processing': processing_jobs
            },
            'training_stats': {
                'total': total_training,
                'completed': completed_training
            },
            'usage': {
                'videos_this_month': user.videos_processed_this_month,
                'total_minutes_processed': user.total_processing_minutes,
                'plan_limits': limits
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Stats error for user {user.id}: {str(e)}")
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500


@api_bp.route('/plans', methods=['GET'])
def get_pricing_plans():
    """Get available pricing plans."""
    return jsonify({
        'plans': {
            'free': {
                'name': 'Free',
                'price': 0,
                'max_video_minutes': 5,
                'max_monthly_videos': 10,
                'features': ['Basic profanity detection', 'Standard censoring modes', 'Email support']
            },
            'pro': {
                'name': 'Pro',
                'price': 29,
                'max_video_minutes': 60,
                'max_monthly_videos': 100,
                'features': ['Advanced profanity detection', 'Custom training', 'All censoring modes', 'Priority support', 'API access']
            },
            'enterprise': {
                'name': 'Enterprise',
                'price': 99,
                'max_video_minutes': 300,
                'max_monthly_videos': 1000,
                'features': ['Everything in Pro', 'NSFW detection', 'White-label options', 'Dedicated support', 'Custom integrations']
            }
        }
    })


# Register additional utility endpoints
@api_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported video formats."""
    return jsonify({
        'video_formats': list(current_app.config['ALLOWED_EXTENSIONS']),
        'max_file_size_mb': current_app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    })


@api_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get comprehensive dashboard data for frontend."""
    user = get_current_user(use_api_key=False)
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get user stats directly (avoiding decorated function)
        total_jobs = Job.query.filter_by(user_id=user.id).count()
        completed_jobs = Job.query.filter_by(user_id=user.id, status='completed').count()
        failed_jobs = Job.query.filter_by(user_id=user.id, status='failed').count()
        pending_jobs = Job.query.filter_by(user_id=user.id, status='pending').count()
        processing_jobs = Job.query.filter_by(user_id=user.id, status='processing').count()
        
        # Count training sessions
        total_training = TrainingSession.query.filter_by(user_id=user.id).count()
        completed_training = TrainingSession.query.filter_by(user_id=user.id, status='completed').count()
        
        # Get plan limits
        limits = user.get_plan_limits()
        
        stats_data = {
            'user': user.to_dict(),
            'job_stats': {
                'total': total_jobs,
                'completed': completed_jobs,
                'failed': failed_jobs,
                'pending': pending_jobs,
                'processing': processing_jobs
            },
            'training_stats': {
                'total': total_training,
                'completed': completed_training
            },
            'usage': {
                'videos_this_month': user.videos_processed_this_month,
                'total_minutes_processed': user.total_processing_minutes,
                'plan_limits': limits
            }
        }
        
        # Get recent jobs
        recent_jobs = Job.query.filter_by(user_id=user.id)\
            .order_by(Job.created_at.desc())\
            .limit(10)\
            .all()
        
        # Get recent training sessions
        recent_training = TrainingSession.query.filter_by(user_id=user.id)\
            .order_by(TrainingSession.created_at.desc())\
            .limit(5)\
            .all()
        
        # Get active/processing jobs
        active_jobs = Job.query.filter_by(user_id=user.id)\
            .filter(Job.status.in_(['pending', 'processing']))\
            .all()
        
        return jsonify({
            'user': stats_data['user'],
            'stats': {
                'jobs': stats_data['job_stats'],
                'training': stats_data['training_stats'],
                'usage': stats_data['usage']
            },
            'recent_jobs': [job.to_dict() for job in recent_jobs],
            'recent_training': [session.to_dict() for session in recent_training],
            'active_jobs': [job.to_dict() for job in active_jobs],
            'plan_limits': user.get_plan_limits()
        })
        
    except Exception as e:
        current_app.logger.error(f"Dashboard data error for user {user.id}: {str(e)}")
        return jsonify({'error': f'Failed to get dashboard data: {str(e)}'}), 500
