"""
Configuration settings for AI Profanity Filter SaaS Platform
Environment-based configuration for development and production.
"""

import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    # Database Configuration (PostgreSQL via Supabase with fallback)
    supabase_db_password = os.environ.get('SUPABASE_DB_PASSWORD')
    supabase_db_host = os.environ.get('SUPABASE_DB_HOST')
    
    if supabase_db_password and supabase_db_host:
        # Try PostgreSQL connection
        try:
            import psycopg2
            SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{supabase_db_password}@{supabase_db_host}:5432/postgres"
        except ImportError:
            # Fallback to SQLite if psycopg2 not available
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///profanity_filter.db'
    else:
        # Use provided DATABASE_URL or fallback to SQLite
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///profanity_filter.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis Configuration (for Celery)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = 'uploads'
    PROCESSED_FOLDER = 'processed'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}
    
    # Storage Configuration
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local')  # 'local' or 's3'
    
    # S3 Configuration (if using S3)
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    
    # User Plan Limits
    FREE_PLAN_VIDEO_LIMIT_MINUTES = 5
    PRO_PLAN_VIDEO_LIMIT_MINUTES = 60
    ENTERPRISE_PLAN_VIDEO_LIMIT_MINUTES = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    DEFAULT_RATE_LIMIT = "100 per hour"
    
    # Processing settings (preserved from original)
    DEFAULT_WHISPER_MODEL = 'medium'  # Options: tiny, base, small, medium, large - medium for better Hindi accuracy
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1  # Mono
    MAX_CONCURRENT_JOBS = 3
    JOB_TIMEOUT = 3600  # 1 hour
    CLEANUP_INTERVAL = 1800  # 30 minutes
    
    # AI Model settings (for future implementation)
    NSFW_MODEL_TYPE = 'nudenet'  # Options: nudenet, custom_cnn
    NSFW_CONFIDENCE_THRESHOLD = 0.6
    FRAME_EXTRACTION_INTERVAL = 1.0  # seconds
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @staticmethod
    def get_user_upload_folder(user_id: int) -> Path:
        """Get user-specific upload folder."""
        return Path(Config.UPLOAD_FOLDER) / str(user_id) / "input"
    
    @staticmethod
    def get_user_processed_folder(user_id: int) -> Path:
        """Get user-specific processed folder."""
        return Path(Config.PROCESSED_FOLDER) / str(user_id) / "output"
    
    @staticmethod
    def get_user_learned_words_path(user_id: int) -> Path:
        """Get user-specific learned words file path."""
        return Path("data/wordlists") / f"learned_words_{user_id}.json"


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    
    # CORS Origins for development
    CORS_ORIGINS = [
        "http://localhost:8080",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8080"
    ]


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    
    # Enforce HTTPS in production
    PREFERRED_URL_SCHEME = 'https'
    
    # More restrictive CORS for production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
