"""
Transcription module for AI Profanity Filter
Handles audio transcription using OpenAI Whisper with timestamps.
"""

import whisper
import os
import re
from typing import Dict, List, Any


def detect_hindi_content(text: str) -> bool:
    """
    Detect if text likely contains Hindi content based on script and common words.
    
    Args:
        text (str): Text to analyze
    
    Returns:
        bool: True if text likely contains Hindi content
    """
    if not text:
        return False
    
    # Check for Devanagari script (Hindi)
    devanagari_pattern = re.compile(r'[\u0900-\u097F]+')
    if devanagari_pattern.search(text):
        return True
    
    # Check for common Hindi words in Latin script
    hindi_indicators = [
        # Common Hindi words
        'hai', 'hain', 'ka', 'ki', 'ke', 'ko', 'se', 'mein', 'aur', 'ek', 'do', 'teen',
        'yeh', 'woh', 'kya', 'kaise', 'kahan', 'kab', 'kyun', 'kyon', 'kaun',
        'main', 'tu', 'aap', 'hum', 'tum', 'wo', 'ye', 'is', 'us',
        'tha', 'thi', 'the', 'hoga', 'hogi', 'honge', 'rahega', 'rahegi',
        'accha', 'theek', 'sahi', 'galat', 'bura', 'achha',
        # Common Hindi greetings and phrases
        'namaste', 'namaskar', 'dhanyawad', 'shukriya', 'maaf', 'kshama',
        'bahut', 'thoda', 'zyada', 'kam', 'sabse', 'sab', 'kuch', 'koi',
        # Hindi profanity indicators (family-friendly detection)
        'bhen', 'chod', 'gand', 'rand', 'kutiya', 'harami', 'sala', 'saala'
    ]
    
    text_lower = text.lower()
    hindi_word_count = sum(1 for word in hindi_indicators if word in text_lower)
    
    # If we find multiple Hindi indicators, likely Hindi content
    return hindi_word_count >= 2


def select_whisper_model_for_content(audio_path: str, default_model: str = "base") -> str:
    """
    Select appropriate Whisper model based on content detection.
    Uses a small initial transcription to detect language, then selects optimal model.
    
    Args:
        audio_path (str): Path to the audio file
        default_model (str): Default model to use for non-Hindi content
    
    Returns:
        str: Model name to use for full transcription
    """
    try:
        # First, do a quick transcription with the base model to detect language
        print("🔍 Detecting language with base model...")
        quick_model = whisper.load_model("base")
        
        # Transcribe for language detection (Whisper automatically detects language)
        quick_result = quick_model.transcribe(
            audio_path,
            word_timestamps=False,
            verbose=False
        )
        
        detected_language = quick_result.get('language', 'unknown')
        transcribed_text = quick_result.get('text', '')
        
        print(f"🌐 Detected language: {detected_language}")
        print(f"📝 Sample text: '{transcribed_text[:100]}{'...' if len(transcribed_text) > 100 else ''}'")
        
        # Check if it's Hindi or contains Hindi content
        is_hindi_by_whisper = detected_language in ['hi', 'hindi']
        is_hindi_by_content = detect_hindi_content(transcribed_text)
        
        print(f"🔍 Hindi by Whisper: {is_hindi_by_whisper}")
        print(f"🔍 Hindi by content analysis: {is_hindi_by_content}")
        
        if is_hindi_by_whisper or is_hindi_by_content:
            print("🇮🇳 Hindi content detected - using 'medium' model for better accuracy")
            return "medium"
        else:
            print(f"🌍 Non-Hindi content detected - using '{default_model}' model")
            return default_model
            
    except Exception as e:
        print(f"⚠️ Error during language detection: {e}")
        print(f"🔄 Falling back to default model: {default_model}")
        return default_model


def transcribe_with_whisper(audio_path: str, model_name: str = "base") -> Dict[str, Any]:
    """
    Transcribe audio using OpenAI Whisper with word-level timestamps.
    Uses the specified model without automatic upgrades to respect subscription tiers.
    
    Args:
        audio_path (str): Path to the audio file
        model_name (str): Whisper model to use ("base", "small", "medium", "large")
                         Note: "auto" is deprecated to enforce subscription-based model selection
    
    Returns:
        Dict containing transcription with segments and word-level timestamps
    
    Raises:
        Exception: If transcription fails
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Use the specified model - no automatic upgrades to respect subscription tiers
        if model_name == "auto":
            print("⚠️ 'auto' model deprecated - using 'base' to respect subscription limits")
            selected_model = "base"
        else:
            selected_model = model_name
        
        print(f"🤖 Loading Whisper model: {selected_model} (subscription-based)")
        model = whisper.load_model(selected_model)
        
        print("🎵 Starting full transcription...")
        # Transcribe with word-level timestamps
        result = model.transcribe(
            audio_path,
            word_timestamps=True,  # Enable word-level timestamps
            verbose=False
        )
        
        # Store the model used in the result for reference
        result['model_used'] = selected_model
        
        print(f"✅ Transcription completed with {selected_model} model")
        print(f"📝 Full text: {result['text'][:100]}...")
        print(f"🎬 Found {len(result.get('segments', []))} segments")
        
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


def force_medium_for_hindi(audio_path: str) -> str:
    """
    Simple approach: Use medium model if we suspect Hindi content.
    This is a more direct approach that doesn't require initial transcription.
    
    Args:
        audio_path (str): Path to the audio file
    
    Returns:
        str: Model name to use ("medium" for suspected Hindi, "base" otherwise)
    """
    # Check filename for Hindi indicators
    filename = os.path.basename(audio_path).lower()
    hindi_filename_indicators = [
        'hindi', 'bhen', 'chu', 'meri', 'ki', 'teri', 'madarchod', 'behenchod',
        'chutiya', 'gandu', 'randi', 'harami', 'sala', 'saala', 'mc', 'bc'
    ]
    
    # If filename suggests Hindi content, use medium model
    for indicator in hindi_filename_indicators:
        if indicator in filename:
            print(f"🇮🇳 Hindi indicator '{indicator}' found in filename - using 'medium' model")
            return "medium"
    
    # Default to base model
    print("🌍 No Hindi indicators in filename - using 'base' model")
    return "base"
