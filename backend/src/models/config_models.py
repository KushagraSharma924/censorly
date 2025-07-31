"""
Configuration models for the AI Profanity Filter.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os


@dataclass
class WhisperConfig:
    """Configuration for Whisper transcription."""
    
    default_model: str = "base"
    hindi_model: str = "medium"
    auto_detect_language: bool = True
    enable_word_timestamps: bool = True
    verbose: bool = False


@dataclass
class ProfanityDetectionConfig:
    """Configuration for profanity detection."""
    
    languages: Optional[List[str]] = None
    adaptive_learning: bool = True
    confidence_threshold: float = 0.8
    max_learned_words: int = 1000
    
    def __post_init__(self):
        if self.languages is None:
            self.languages = ["english", "hindi_latin", "hindi_devanagari", "hindi_urdu_script"]


@dataclass
class CensoringConfig:
    """Configuration for audio censoring."""
    
    beep_frequency: int = 1000
    beep_volume: float = 0.5
    fade_duration: float = 0.1
    padding_before: float = 0.1
    padding_after: float = 0.1


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # Directories
    upload_dir: str = "uploads"
    processed_dir: str = "processed"
    data_dir: str = "data"
    logs_dir: str = "logs"
    
    # File limits
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: Optional[List[str]] = None
    
    # Processing
    whisper: Optional[WhisperConfig] = None
    profanity: Optional[ProfanityDetectionConfig] = None
    censoring: Optional[CensoringConfig] = None
    
    # API
    flask_debug: bool = False
    flask_port: int = 9001
    cors_origins: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        if self.whisper is None:
            self.whisper = WhisperConfig()
        if self.profanity is None:
            self.profanity = ProfanityDetectionConfig()
        if self.censoring is None:
            self.censoring = CensoringConfig()
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:5173", "http://localhost:3000"]
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        return cls(
            upload_dir=os.getenv('UPLOAD_DIR', 'uploads'),
            processed_dir=os.getenv('PROCESSED_DIR', 'processed'),
            flask_debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            flask_port=int(os.getenv('PORT', '9001')),
            max_file_size=int(os.getenv('MAX_FILE_SIZE', str(100 * 1024 * 1024)))
        )
