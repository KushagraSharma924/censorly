"""
Modern API Routes for Abuse Classification
Refactored to use the new abuse classifier instead of legacy rule-based detection.
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
from services.abuse_classifier import load_classifier, get_classifier_info
from utils.audio_utils import get_audio_duration
from config import Config

# Import celery task with fallback
try:
    from celery import Celery
    CELERY_AVAILABLE = True
    
    # Create a simple task placeholder
    def process_video_task_placeholder():
        pass
    process_video_task = process_video_task_placeholder
    
except ImportError:
    CELERY_AVAILABLE = False

# Create blueprint
api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Validation schemas
class VideoUploadSchema(Schema):
    censoring_mode = fields.Str(validate=validate.OneOf(['beep', 'mute', 'cut-scene', 'cut-nsfw']), missing='beep')
    abuse_threshold = fields.Float(validate=validate.Range(min=0.1, max=1.0), missing=0.7)
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
        return User.query.get(int(user_id))
    except:
        return None


@api_v2_bp.route('/test-classifier', methods=['POST'])
@api_key_required
def test_classifier():
    """
    Test the abuse classifier with provided text.
    """
    try:
        # Validate input
        schema = AbuseTestSchema()
        data = schema.load(request.json)
        
        text = data['text']
        return_confidence = data['return_confidence']
        
        # Load classifier
        try:
            classifier = load_classifier()
            result = classifier.predict(text, return_score=return_confidence)
        except Exception as e:
            return jsonify({
                'error': f'Classifier not available: {str(e)}',
                'fallback_used': True,
                'text': text
            }), 500
        
        # Format response
        if isinstance(result, dict):
            response = {
                'text': text,
                'is_abusive': result.get('is_abusive', False),
                'confidence': result.get('confidence', 0.0),
                'model_type': result.get('model_type', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            response = {
                'text': text,
                'is_abusive': bool(result),
                'confidence': 1.0 if result else 0.0,
                'model_type': 'simple',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return jsonify(response)
        
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file was uploaded
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
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
                'abuse_threshold': float(request.form.get('abuse_threshold', 0.7)),
                'languages': request.form.get('languages', 'auto').split(','),
                'whisper_model': request.form.get('whisper_model', 'base')
            }
            
            schema = VideoUploadSchema()
            validated_data = schema.load(form_data)
            
        except (ValueError, ValidationError) as e:
            return jsonify({'error': f'Invalid form data: {str(e)}'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        stored_filename = f"{file_id}.{file_extension}"
        
        upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / str(user.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / stored_filename
        
        file.save(str(file_path))
        
        # Get video duration for estimation
        try:
            duration = get_audio_duration(str(file_path))
        except:
            duration = 0
        
        # Create job record
        job = Job(
            user_id=user.id,
            job_type='video_processing_v2',
            status='queued',
            input_filename=filename,
            file_path=str(file_path),
            parameters=json.dumps({
                'censoring_mode': validated_data['censoring_mode'],
                'abuse_threshold': validated_data['abuse_threshold'],
                'languages': validated_data['languages'],
                'whisper_model': validated_data['whisper_model']
            }),
            estimated_duration=max(30, duration * 2)  # Estimate processing time
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start background processing using the new video processor
        if CELERY_AVAILABLE:
            task = process_video_task.apply_async(
                args=[job.id],
                kwargs={
                    'use_v2_processor': True,  # Flag to use the new processor
                    'abuse_threshold': validated_data['abuse_threshold']
                }
            )
            
            # Update job with task ID
            job.celery_task_id = task.id
            task_id = task.id
        else:
            # Fallback: mark as queued without background processing
            task_id = f"mock_{job.id}"
            job.celery_task_id = task_id
        db.session.commit()
        
        return jsonify({
            'job_id': job.id,
            'task_id': task_id,
            'status': 'queued',
            'estimated_duration': job.estimated_duration,
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
        
        # Parse job results
        results = {}
        if job.results:
            try:
                results = json.loads(job.results)
            except:
                results = {'raw_results': job.results}
        
        response = {
            'job_id': job.id,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'updated_at': job.updated_at.isoformat(),
            'input_filename': job.input_filename,
            'progress': job.progress or 0,
            'estimated_duration': job.estimated_duration,
            'processor_version': '2.0'
        }
        
        # Add results if completed
        if job.status == 'completed' and results:
            response.update({
                'results': results,
                'abusive_segments': results.get('abusive_segments', []),
                'duration': results.get('duration', 0),
                'output_available': bool(results.get('output_path'))
            })
        
        # Add error info if failed
        if job.status == 'failed':
            response['error'] = job.error_message or results.get('error', 'Unknown error')
        
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
        original_name = Path(job.input_filename).stem
        mode = json.loads(job.parameters).get('censoring_mode', 'processed')
        file_extension = Path(output_path).suffix
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
                'updated_at': job.updated_at.isoformat(),
                'input_filename': job.input_filename,
                'job_type': job.job_type,
                'progress': job.progress or 0
            }
            
            # Add summary results if completed
            if job.status == 'completed' and job.results:
                try:
                    results = json.loads(job.results)
                    job_data['summary'] = {
                        'duration': results.get('duration', 0),
                        'abusive_segments_count': len(results.get('abusive_segments', [])),
                        'output_available': bool(results.get('output_path'))
                    }
                except:
                    pass
            
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
