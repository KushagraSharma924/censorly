"""
Database models for AI Profanity Filter SaaS Platform
SQLAlchemy models for users, jobs, and authentication.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
import uuid
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and user management."""
    
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User profile
    full_name = db.Column(db.String(100))
    subscription_tier = db.Column(db.String(20), default='free')  # free, premium, enterprise
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Usage tracking
    videos_processed = db.Column(db.Integer, default=0)
    total_processing_time = db.Column(db.Float, default=0.0)
    
    # Relationships
    jobs = db.relationship('Job', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    training_sessions = db.relationship('TrainingSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email, full_name=None, subscription_tier='free'):
        self.email = email
        self.full_name = full_name
        self.subscription_tier = subscription_tier
    
    def get_plan_limits(self):
        """Get plan-specific limits."""
        limits = {
            'free': {'max_video_minutes': 5, 'max_monthly_videos': 10},
            'premium': {'max_video_minutes': 60, 'max_monthly_videos': 100},
            'enterprise': {'max_video_minutes': 300, 'max_monthly_videos': 1000}
        }
        return limits.get(self.subscription_tier, limits['free'])
    
    def can_process_video(self, duration_minutes):
        """Check if user can process a video of given duration."""
        limits = self.get_plan_limits()
        return duration_minutes <= limits['max_video_minutes']
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'plan': self.plan,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'videos_processed_this_month': self.videos_processed_this_month,
            'total_processing_minutes': self.total_processing_minutes,
            'plan_limits': self.get_plan_limits()
        }


class Job(db.Model):
    """Job model for tracking video processing tasks."""
    
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Job details
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    duration = db.Column(db.Float)  # in seconds
    
    # Processing configuration
    censoring_mode = db.Column(db.String(20), default='beep')  # beep, mute, cut
    profanity_threshold = db.Column(db.Float, default=0.8)
    languages = db.Column(db.Text)  # JSON string of language codes
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # File paths
    input_path = db.Column(db.String(500))
    output_path = db.Column(db.String(500))
    
    # Results
    profane_segments_count = db.Column(db.Integer, default=0)
    censored_duration = db.Column(db.Float, default=0.0)  # seconds of censored content
    result_url = db.Column(db.String(500))
    download_url = db.Column(db.String(500))
    
    # Error handling
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # when files will be deleted
    
    # Celery task ID
    celery_task_id = db.Column(db.String(255))
    
    @property
    def processing_time(self):
        """Get processing time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self):
        """Convert job to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'duration': self.duration,
            'censoring_mode': self.censoring_mode,
            'profanity_threshold': self.profanity_threshold,
            'languages': self.languages,
            'status': self.status,
            'progress': self.progress,
            'profane_segments_count': self.profane_segments_count,
            'censored_duration': self.censored_duration,
            'result_url': self.result_url,
            'download_url': self.download_url,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'processing_time': self.processing_time
        }


class TrainingSession(db.Model):
    """Training session model for custom dataset training."""
    
    __tablename__ = 'training_sessions'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Training details
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    total_words = db.Column(db.Integer, default=0)
    new_words_added = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)
    
    # Results
    training_summary = db.Column(db.Text)  # JSON string with training details
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Celery task ID
    celery_task_id = db.Column(db.String(255))
    
    def to_dict(self):
        """Convert training session to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'total_words': self.total_words,
            'new_words_added': self.new_words_added,
            'status': self.status,
            'progress': self.progress,
            'training_summary': self.training_summary,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
