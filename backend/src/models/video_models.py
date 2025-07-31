"""
Data models for video processing results and metadata.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class VideoProcessingResult:
    """Result of video processing operation."""
    
    status: str
    input_file: str
    output_file: Optional[str] = None
    processing_time: float = 0.0
    model_used: Optional[str] = None
    segments_processed: int = 0
    profane_segments_detected: int = 0
    profane_segments_censored: int = 0
    steps_completed: Optional[List[str]] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio with timestamps."""
    
    text: str
    start: float
    end: float
    id: Optional[str] = None
    words: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        if self.words is None:
            self.words = []


@dataclass
class ProfanityMatch:
    """A detected profane word or phrase."""
    
    word: str
    language: str
    start_time: float
    end_time: float
    confidence: float = 1.0
    original_text: str = ""
    segment_id: Optional[str] = None


@dataclass
class TranscriptionResult:
    """Complete transcription result with metadata."""
    
    text: str
    language: str
    model_used: str
    segments: List[TranscriptionSegment]
    processing_time: float = 0.0
    confidence: float = 0.0
    
    def get_segments_by_timerange(self, start: float, end: float) -> List[TranscriptionSegment]:
        """Get segments within a specific time range."""
        return [
            segment for segment in self.segments
            if segment.start >= start and segment.end <= end
        ]


@dataclass
class CensoringResult:
    """Result of audio censoring operation."""
    
    input_file: str
    output_file: str
    segments_censored: List[Dict[str, Any]]
    total_duration: float
    censored_duration: float
    success: bool = True
    error_message: Optional[str] = None
