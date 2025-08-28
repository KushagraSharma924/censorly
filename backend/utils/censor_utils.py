"""
Censoring utilities for ai-profanity-filter
Handles profanity detection and audio censoring using better-profanity and pydub.
"""

from better_profanity import profanity
from pydub import AudioSegment
from pydub.generators import Sine
import os
import numpy as np
import wave
from typing import Dict, List, Any, Tuple


def initialize_profanity_filter():
    """Initialize the profanity filter with default settings."""
    profanity.load_censor_words()


def detect_profane_words(text: str) -> List[str]:
    """
    Detect profane words in a given text.
    
    Args:
        text (str): Text to check for profanity
    
    Returns:
        List of profane words found
    """
    words = text.lower().split()
    profane_words = []
    
    for word in words:
        # Clean the word of punctuation for better detection
        clean_word = ''.join(char for char in word if char.isalnum())
        if profanity.contains_profanity(clean_word):
            profane_words.append(word)
    
    return profane_words


def find_profane_segments(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find segments containing profane words with their timestamps.
    Prioritizes word-level timestamps for precise censoring.
    
    Args:
        transcript_data: Whisper transcription result
    
    Returns:
        List of dictionaries with profane segments and timestamps
    """
    initialize_profanity_filter()
    profane_segments = []
    
    # First priority: Check word-level timestamps if available
    word_level_found = False
    for segment in transcript_data.get('segments', []):
        for word_info in segment.get('words', []):
            word = word_info['word'].strip()
            # Clean the word of punctuation for better detection
            clean_word = ''.join(char for char in word if char.isalnum())
            if clean_word and detect_profane_words(clean_word):
                profane_segments.append({
                    'text': word,
                    'start': word_info['start'],
                    'end': word_info['end'],
                    'profane_words': [clean_word],
                    'type': 'word'
                })
                word_level_found = True
    
    # If no word-level timestamps found, fall back to segment-level
    if not word_level_found:
        print("⚠️  No word-level timestamps found, using segment-level censoring")
        for segment in transcript_data.get('segments', []):
            segment_text = segment['text'].strip()
            profane_words = detect_profane_words(segment_text)
            
            if profane_words:
                profane_segments.append({
                    'text': segment_text,
                    'start': segment['start'],
                    'end': segment['end'],
                    'profane_words': profane_words,
                    'type': 'segment'
                })
    
    # Remove duplicates and sort by start time
    unique_segments = []
    seen_times = set()
    
    for segment in profane_segments:
        time_key = (round(segment['start'], 3), round(segment['end'], 3))
        if time_key not in seen_times:
            seen_times.add(time_key)
            unique_segments.append(segment)
    
    unique_segments.sort(key=lambda x: x['start'])
    return unique_segments


def create_beep_sound(duration_ms: int, frequency: int = 1000) -> AudioSegment:
    """
    Create a beep sound of specified duration.
    
    Args:
        duration_ms (int): Duration in milliseconds
        frequency (int): Frequency of the beep in Hz
    
    Returns:
        AudioSegment containing the beep sound
    """
    # Generate sine wave beep
    beep = Sine(frequency).to_audio_segment(duration=duration_ms)
    
    # Apply fade in/out to avoid clicking sounds
    beep = beep.fade_in(10).fade_out(10)
    
    # Reduce volume to 50% to make it less harsh
    beep = beep - 6  # Reduce by 6dB
    
    return beep


def censor_audio_segment(audio: AudioSegment, start_time: float, end_time: float, 
                        censor_type: str = "mute") -> AudioSegment:
    """
    Censor a specific segment of audio.
    
    Args:
        audio (AudioSegment): Original audio
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        censor_type (str): Type of censoring - "mute" or "beep" (default: "mute")
    
    Returns:
        AudioSegment with censored portion
    """
    # Convert times to milliseconds
    start_ms = int(start_time * 1000)
    end_ms = int(end_time * 1000)
    
    # Ensure we don't go beyond audio bounds
    start_ms = max(0, start_ms)
    end_ms = min(len(audio), end_ms)
    
    if start_ms >= end_ms:
        return audio
    
    # Split audio into before, during, and after segments
    before = audio[:start_ms]
    during = audio[start_ms:end_ms]
    after = audio[end_ms:]
    
    if censor_type == "mute":
        # Replace with silence
        censored_segment = AudioSegment.silent(duration=len(during))
    else:  # beep
        # Replace with beep sound
        censored_segment = create_beep_sound(len(during))
        
        # Match the original audio's properties
        if len(during) > 0:
            censored_segment = censored_segment.set_channels(during.channels)
            censored_segment = censored_segment.set_frame_rate(during.frame_rate)
    
    # Combine all segments
    return before + censored_segment + after


def detect_and_censor_audio(audio_path: str, transcript_data: Dict[str, Any], 
                           output_path: str, censor_type: str = "mute") -> int:
    """
    Main function to detect profane words and censor the audio.
    
    Args:
        audio_path (str): Path to the original audio file
        transcript_data: Whisper transcription result
        output_path (str): Path to save the censored audio
        censor_type (str): Type of censoring - "mute" or "beep" (default: "mute")
    
    Returns:
        int: Number of segments censored
    
    Raises:
        Exception: If audio processing fails
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print("Detecting profane segments...")
        profane_segments = find_profane_segments(transcript_data)
        
        if not profane_segments:
            print("No profane words detected. Copying original audio.")
            # Copy original file if no processing needed
            import shutil
            shutil.copy2(audio_path, output_path)
            return 0
        
        print(f"Found {len(profane_segments)} profane segments to censor:")
        for segment in profane_segments:
            segment_type = "word" if segment['type'] == 'word' else "segment"
            duration = segment['end'] - segment['start']
            print(f"  - {segment_type}: '{segment['text']}' at {segment['start']:.2f}s-{segment['end']:.2f}s ({duration:.2f}s)")
        
        print("Loading audio file...")
        audio = AudioSegment.from_file(audio_path)
        
        # Apply censoring to each segment
        censored_audio = audio
        for segment in profane_segments:
            censored_audio = censor_audio_segment(
                censored_audio,
                segment['start'],
                segment['end'],
                censor_type
            )
        
        print(f"Exporting censored audio with {censor_type} censoring to: {output_path}")
        censored_audio.export(output_path, format="wav")
        
        return len(profane_segments)
        
    except Exception as e:
        raise Exception(f"Error during audio censoring: {e}")


def add_custom_profanity_words(custom_words: List[str]):
    """
    Add custom words to the profanity filter.
    
    Args:
        custom_words (List[str]): List of words to add to the filter
    """
    for word in custom_words:
        profanity.add_censor_words([word])


