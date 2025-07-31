"""
Configuration file for AI Profanity Filter
Centralized settings for the application
"""

import os
from pathlib import Path
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.config_models import AppConfig


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB
    
    # Directory settings
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    PROCESSED_FOLDER = BASE_DIR / 'processed'
    TEMP_FOLDER = BASE_DIR / 'temp'
    
    # File handling
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv', 'm4v'}
    
    # Processing settings
    DEFAULT_WHISPER_MODEL = 'base'  # Options: tiny, base, small, medium, large
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1  # Mono
    
    # Job management
    MAX_CONCURRENT_JOBS = 3
    JOB_TIMEOUT = 3600  # 1 hour
    CLEANUP_INTERVAL = 1800  # 30 minutes
    
    # AI Model settings (for future implementation)
    NSFW_MODEL_TYPE = 'nudenet'  # Options: nudenet, custom_cnn
    NSFW_CONFIDENCE_THRESHOLD = 0.6
    FRAME_EXTRACTION_INTERVAL = 1.0  # seconds
    
    # Custom profanity words (can be extended)
    CUSTOM_PROFANITY_WORDS = [
        # Add your custom words here
    ]
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def init_app(cls, app):
        """Initialize the Flask app with configuration"""
        # Create necessary directories
        for folder in [cls.UPLOAD_FOLDER, cls.PROCESSED_FOLDER, cls.TEMP_FOLDER]:
            folder.mkdir(exist_ok=True)


    @staticmethod
    def setup_directories(config: 'AppConfig') -> None:
        """Create necessary directories if they don't exist."""
        
        directories = [
            config.upload_dir,
            config.processed_dir,
            config.data_dir,
            config.logs_dir,
            f"{config.data_dir}/models",
            f"{config.data_dir}/wordlists"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"📁 Ensured directory exists: {directory}")


    @staticmethod
    def setup_logging(logs_dir: str) -> None:
        """Setup application logging."""
        
        log_file = Path(logs_dir) / "app.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Reduce noise from external libraries
        logging.getLogger('whisper').setLevel(logging.WARNING)
        logging.getLogger('ffmpeg').setLevel(logging.WARNING)
        
        print(f"📋 Logging configured: {log_file}")


    @staticmethod
    def get_env_config() -> dict:
        """Get configuration from environment variables."""
        
        return {
            'upload_dir': os.getenv('UPLOAD_DIR', 'uploads'),
            'processed_dir': os.getenv('PROCESSED_DIR', 'processed'),
            'flask_debug': os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            'flask_port': int(os.getenv('PORT', '9001')),
            'max_file_size': int(os.getenv('MAX_FILE_SIZE', str(100 * 1024 * 1024)))
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Stricter limits for production
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    MAX_CONCURRENT_JOBS = 5


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Smaller limits for testing
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
