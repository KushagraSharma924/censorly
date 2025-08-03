#!/usr/bin/env python
"""
Celery worker configuration for AI Profanity Filter
"""

import os
import sys
from celery import Celery
from kombu import Queue

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Import Flask app
from app import create_app

# Celery configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Fallback to memory for development if Redis is not available
try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
except:
    # Use in-memory transport for development
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

# Create Celery instance
celery = Celery('ai_profanity_filter')

# Configure Celery
celery.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'services.celery_worker.process_video_task': {'queue': 'video_processing'},
    },
    task_default_queue='default',
    task_queues=(
        Queue('default'),
        Queue('video_processing', routing_key='video_processing'),
    ),
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
)

# Create Flask app context for tasks
flask_app = create_app()

@celery.task(bind=True, name='services.celery_worker.process_video_task')
def process_video_task(self, job_id, input_path, mode, abuse_threshold=0.7, whisper_model='base'):
    """
    Celery task to process video files with profanity detection.
    
    Args:
        job_id (str): UUID of the job
        input_path (str): Path to the input video file
        mode (str): Processing mode ('beep', 'mute', 'cut-scene', 'cut-nsfw')
        abuse_threshold (float): Threshold for abuse detection
        whisper_model (str): Whisper model to use
    
    Returns:
        dict: Processing results
    """
    with flask_app.app_context():
        try:
            from models.saas_models import Job, db
            from video_processor_v2 import process_video
            from datetime import datetime
            import time
            
            # Update task state
            self.update_state(state='PROGRESS', meta={'status': 'Starting video processing'})
            
            # Get job from database
            job = db.session.get(Job, job_id)
            if not job:
                raise Exception(f"Job {job_id} not found")
            
            # Update job status
            job.status = 'processing'
            db.session.commit()
            
            self.update_state(state='PROGRESS', meta={'status': 'Processing video with AI'})
            
            # Process the video
            start_time = time.time()
            
            # Set up output directory
            from pathlib import Path
            output_dir = Path(input_path).parent / "processed"
            output_dir.mkdir(exist_ok=True)
            
            # Process video with AI
            processing_result = process_video(
                input_path=input_path,
                mode=mode,
                temp_dir=str(output_dir),
                abuse_threshold=abuse_threshold,
                whisper_model=whisper_model
            )
            
            processing_time = time.time() - start_time
            
            # Update job with results
            if processing_result.get('output_path'):
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
                job.output_path = processing_result['output_path']
                job.processing_time = processing_time
                job.profane_segments_count = len(processing_result.get('abusive_segments', []))
                job.download_url = f"/api/download/{job.id}"
                
                result = {
                    'status': 'completed',
                    'job_id': job_id,
                    'output_path': processing_result['output_path'],
                    'processing_time': processing_time,
                    'profane_segments_count': job.profane_segments_count,
                    'download_url': job.download_url
                }
            else:
                job.status = 'failed'
                job.error_message = "Video processing failed - no output generated"
                result = {
                    'status': 'failed',
                    'job_id': job_id,
                    'error': 'No output generated'
                }
            
            db.session.commit()
            
            self.update_state(
                state='SUCCESS',
                meta=result
            )
            
            return result
            
        except Exception as e:
            # Update job status on failure
            try:
                job = db.session.get(Job, job_id)
                if job:
                    job.status = 'failed'
                    job.error_message = str(e)
                    db.session.commit()
            except:
                pass
            
            self.update_state(
                state='FAILURE',
                meta={
                    'status': 'failed',
                    'job_id': job_id,
                    'error': str(e)
                }
            )
            raise


if __name__ == '__main__':
    celery.start()
