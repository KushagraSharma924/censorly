"""
Enhanced SaaS Models for AI Profanity Filter Platform
Comprehensive database models for user management, authentication, billing, and job tracking.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import secrets
import string

db = SQLAlchemy()

class User(db.Model):
    """Enhanced User model with SaaS features."""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Subscription info
    subscription_tier = db.Column(db.String(20), default='free')
    
    # Usage tracking
    videos_processed = db.Column(db.Integer, default=0)
    total_processing_time = db.Column(db.Float, default=0.0)  # in minutes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    jobs = db.relationship('Job', backref='user', lazy='dynamic')
    training_sessions = db.relationship('TrainingSession', backref='user', lazy='dynamic')
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_plan_limits(self):
        """Get plan limits based on subscription tier."""
        plans = {
            'free': {
                'monthly_limit': 10,
                'max_file_size_mb': 100,
                'max_video_minutes': 5,
                'features': ['basic_detection']
            },
            'basic': {
                'monthly_limit': 100,
                'max_file_size_mb': 500,
                'max_video_minutes': 30,
                'features': ['basic_detection', 'api_access']
            },
            'pro': {
                'monthly_limit': 500,
                'max_file_size_mb': 1000,
                'max_video_minutes': 60,
                'features': ['advanced_detection', 'api_access', 'priority_processing']
            },
            'enterprise': {
                'monthly_limit': -1,  # Unlimited
                'max_file_size_mb': 5000,
                'max_video_minutes': 180,
                'features': ['all_features', 'dedicated_support']
            }
        }
        return plans.get(self.subscription_tier, plans['free'])
    
    def get_active_subscription(self):
        """Get user's active subscription."""
        return self.subscriptions.filter_by(is_active=True).first()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'subscription_tier': self.subscription_tier,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'videos_processed': self.videos_processed,
            'total_processing_time': self.total_processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Job(db.Model):
    """Job model for tracking video processing tasks."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Job details
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    duration = db.Column(db.Float)  # in seconds
    
    # Processing configuration
    censoring_mode = db.Column(db.String(20), default='beep')
    profanity_threshold = db.Column(db.Float, default=0.8)
    languages = db.Column(db.Text)  # JSON string
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # File paths
    input_path = db.Column(db.String(500))
    output_path = db.Column(db.String(500))
    
    # Results
    profane_segments_count = db.Column(db.Integer, default=0)
    processing_time = db.Column(db.Float)  # in seconds
    download_url = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Celery task ID
    celery_task_id = db.Column(db.String(255))
    
    def to_dict(self):
        """Convert job to dictionary."""
        return {
            'id': self.id,
            'user_id': str(self.user_id),
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'duration': self.duration,
            'censoring_mode': self.censoring_mode,
            'profanity_threshold': self.profanity_threshold,
            'languages': self.languages,
            'status': self.status,
            'progress': self.progress,
            'profane_segments_count': self.profane_segments_count,
            'processing_time': self.processing_time,
            'download_url': self.download_url,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class APIKey(db.Model):
    """API Key model for programmatic access."""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    key_prefix = db.Column(db.String(10))  # First 10 chars for display
    key_hash = db.Column(db.String(128), nullable=False)
    
    # Status and limits
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Store raw key temporarily during creation
    _raw_key = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate API key during initialization
        self._raw_key = self._generate_api_key()
        self.key_prefix = self._raw_key[:10]
        self.key_hash = generate_password_hash(self._raw_key)
    
    def _generate_api_key(self):
        """Generate a new API key."""
        return f"apf_{secrets.token_urlsafe(32)}"
    
    def get_raw_key(self):
        """Get the raw API key (only available during creation)."""
        if self._raw_key:
            return self._raw_key
        raise ValueError("Raw key only available during creation")
    
    @classmethod
    def verify_key(cls, raw_key):
        """Verify an API key and return the APIKey object if valid."""
        api_keys = cls.query.filter_by(is_active=True).all()
        for key_obj in api_keys:
            if check_password_hash(key_obj.key_hash, raw_key):
                return key_obj
        return None
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'key_prefix': self.key_prefix,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat()
        }

class Subscription(db.Model):
    """Subscription model for billing and plan management."""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Plan details
    plan_name = db.Column(db.String(50), nullable=False)
    plan_price = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, active, cancelled, expired
    is_active = db.Column(db.Boolean, default=False)
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Razorpay integration
    razorpay_subscription_id = db.Column(db.String(100))
    razorpay_customer_id = db.Column(db.String(100))
    razorpay_order_id = db.Column(db.String(100))
    razorpay_payment_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    def is_expired(self):
        """Check if subscription is expired."""
        if self.end_date:
            return datetime.utcnow() > self.end_date
        return False
    
    def cancel(self):
        """Cancel the subscription."""
        self.status = 'cancelled'
        self.is_active = False
        self.cancelled_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert subscription to dictionary."""
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'plan_price': self.plan_price,
            'status': self.status,
            'is_active': self.is_active,
            'auto_renew': self.auto_renew,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_expired': self.is_expired()
        }

class TrainingSession(db.Model):
    """Training session model for custom dataset training."""
    __tablename__ = 'training_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Training details
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    total_words = db.Column(db.Integer, default=0)
    new_words_added = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default='pending')
    progress = db.Column(db.Integer, default=0)
    
    # Results
    training_summary = db.Column(db.Text)  # JSON string
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Celery task ID
    celery_task_id = db.Column(db.String(255))
    
    def to_dict(self):
        """Convert training session to dictionary."""
        return {
            'id': self.id,
            'user_id': str(self.user_id),
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'total_words': self.total_words,
            'new_words_added': self.new_words_added,
            'status': self.status,
            'progress': self.progress,
            'training_summary': self.training_summary,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
