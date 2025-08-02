"""
Data models for AI Profanity Filter
Classes for representing video processing data and configurations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class VideoSegment:
    """Represents a segment of video with timing information."""
    start: float
    end: float
    text: str = ""
    confidence: float = 1.0
    language: str = "unknown"
    
    @property
    def duration(self) -> float:
        """Get the duration of the segment in seconds."""
        return self.end - self.start


@dataclass
class ProfaneSegment:
    """Represents a profane segment that needs censoring."""
    start: float
    end: float
    profane_words: List[str]
    text: str = ""
    confidence: float = 1.0
    language: str = "unknown"
    severity: str = "medium"  # low, medium, high
    detection_method: str = "word_list"  # word_list, ai_model, manual
    
    @property
    def duration(self) -> float:
        """Get the duration of the segment in seconds."""
        return self.end - self.start
    
    @property
    def word_count(self) -> int:
        """Get the number of profane words detected."""
        return len(self.profane_words)


@dataclass
class ProcessingJob:
    """Represents a video processing job."""
    job_id: str
    input_path: Path
    mode: str
    status: str = "pending"
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    custom_words: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.custom_words is None:
            self.custom_words = []
        if self.start_time is None:
            self.start_time = datetime.now()


@dataclass
class ProcessingResult:
    """Represents the result of video processing."""
    job_id: str
    original_path: Path
    output_path: Optional[Path] = None
    profane_segments: Optional[List[ProfaneSegment]] = None
    nsfw_segments: Optional[List[VideoSegment]] = None
    processing_time: float = 0.0
    total_duration: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.profane_segments is None:
            self.profane_segments = []
        if self.nsfw_segments is None:
            self.nsfw_segments = []
    
    @property
    def profane_count(self) -> int:
        """Get the total number of profane segments."""
        return len(self.profane_segments) if self.profane_segments else 0
    
    @property
    def total_profane_words(self) -> int:
        """Get the total number of profane words detected."""
        return sum(segment.word_count for segment in self.profane_segments) if self.profane_segments else 0
    
    @property
    def censored_duration(self) -> float:
        """Get the total duration of censored content in seconds."""
        return sum(segment.duration for segment in self.profane_segments) if self.profane_segments else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'job_id': self.job_id,
            'original_path': str(self.original_path),
            'output_path': str(self.output_path) if self.output_path else None,
            'profane_segments': [
                {
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text,
                    'profane_words': seg.profane_words,
                    'severity': seg.severity,
                    'detection_method': seg.detection_method
                }
                for seg in self.profane_segments
            ] if self.profane_segments else [],
            'nsfw_segments': [
                {
                    'start': seg.start,
                    'end': seg.end,
                    'confidence': seg.confidence
                }
                for seg in self.nsfw_segments
            ] if self.nsfw_segments else [],
            'processing_time': self.processing_time,
            'total_duration': self.total_duration,
            'profane_count': self.profane_count,
            'total_profane_words': self.total_profane_words,
            'censored_duration': self.censored_duration,
            'success': self.success,
            'error_message': self.error_message
        }


@dataclass
class AppConfig:
    """Application configuration."""
    max_file_size: int = 200 * 1024 * 1024  # 200MB
    allowed_extensions: Optional[List[str]] = None
    upload_folder: Path = Path('uploads')
    processed_folder: Path = Path('processed')
    whisper_model: str = "base"
    enable_nsfw_detection: bool = False
    cors_origins: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v']
        if self.cors_origins is None:
            self.cors_origins = [
                "http://localhost:8080",
                "http://localhost:5173", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173"
            ]
