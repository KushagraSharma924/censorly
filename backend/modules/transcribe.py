"""
Transcription module for AI Profanity Filter
Handles audio transcription using OpenAI Whisper with timestamps.
"""

import whisper
import os
from typing import Dict, List, Any


def transcribe_with_whisper(audio_path: str, model_name: str = "base") -> Dict[str, Any]:
    """
    Transcribe audio using OpenAI Whisper with word-level timestamps.
    
    Args:
        audio_path (str): Path to the audio file
        model_name (str): Whisper model to use (base, small, medium, large)
    
    Returns:
        Dict containing transcription with segments and word-level timestamps
    
    Raises:
        Exception: If transcription fails
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name)
        
        print("Starting transcription...")
        # Transcribe with word-level timestamps
        result = model.transcribe(
            audio_path,
            word_timestamps=True,  # Enable word-level timestamps
            verbose=False
        )
        
        print(f"Transcription completed. Text: {result['text'][:100]}...")
        
        return result
        
    except Exception as e:
        raise Exception(f"Error during transcription: {e}")


def get_word_timestamps(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract word-level timestamps from Whisper transcription result.
    
    Args:
        transcript_data: Result from whisper.transcribe()
    
    Returns:
        List of dictionaries with word, start, and end timestamps
    """
    words_with_timestamps = []
    
    try:
        for segment in transcript_data.get('segments', []):
            for word_info in segment.get('words', []):
                words_with_timestamps.append({
                    'word': word_info['word'].strip(),
                    'start': word_info['start'],
                    'end': word_info['end']
                })
    except KeyError as e:
        print(f"Warning: Expected key not found in transcript data: {e}")
    
    return words_with_timestamps


def get_segment_timestamps(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract segment-level timestamps from Whisper transcription result.
    
    Args:
        transcript_data: Result from whisper.transcribe()
    
    Returns:
        List of dictionaries with text, start, and end timestamps
    """
    segments_with_timestamps = []
    
    try:
        for segment in transcript_data.get('segments', []):
            segments_with_timestamps.append({
                'text': segment['text'].strip(),
                'start': segment['start'],
                'end': segment['end']
            })
    except KeyError as e:
        print(f"Warning: Expected key not found in transcript data: {e}")
    
    return segments_with_timestamps


def save_transcript_to_file(transcript_data: Dict[str, Any], output_path: str):
    """
    Save transcription result to a text file.
    
    Args:
        transcript_data: Result from whisper.transcribe()
        output_path: Path to save the transcript file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== FULL TRANSCRIPT ===\n")
            f.write(transcript_data['text'])
            f.write("\n\n=== SEGMENTS WITH TIMESTAMPS ===\n")
            
            for segment in transcript_data.get('segments', []):
                start_time = format_timestamp(segment['start'])
                end_time = format_timestamp(segment['end'])
                f.write(f"[{start_time} -> {end_time}] {segment['text']}\n")
                
    except Exception as e:
        print(f"Warning: Could not save transcript to file: {e}")


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp from seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string (MM:SS)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
