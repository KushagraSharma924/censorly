"""
Word detection module for AI Profanity Filter
Handles profanity detection using better-profanity library.
"""

from better_profanity import profanity
from typing import Dict, List, Any


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


def detect_abusive_words(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
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


def add_custom_profanity_words(custom_words: List[str]):
    """
    Add custom words to the profanity filter.
    
    Args:
        custom_words (List[str]): List of words to add to the filter
    """
    for word in custom_words:
        profanity.add_censor_words([word])


def test_profanity_detection(text: str) -> Dict[str, Any]:
    """
    Test function to check profanity detection on a given text.
    
    Args:
        text (str): Text to test
    
    Returns:
        Dictionary with detection results
    """
    initialize_profanity_filter()
    
    return {
        'original_text': text,
        'contains_profanity': profanity.contains_profanity(text),
        'censored_text': profanity.censor(text),
        'detected_words': detect_profane_words(text)
    }
