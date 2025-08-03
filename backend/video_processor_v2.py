"""
Refactored Video Processor for Modern Abuse Classification
Removes legacy profanity detection and integrates with the new abuse classifier.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our modular components
from services.transcription import transcribe_with_whisper
from services.abuse_classifier import load_classifier
from services.nsfw_detection import detect_nsfw_scenes
from utils.ffmpeg_tools import (
    extract_audio, merge_audio_to_video, apply_beep, apply_mute, cut_scenes,
    apply_beep_to_video, apply_mute_to_video, get_video_duration, validate_video_file
)


def process_video(input_path: str, mode: str, temp_dir: Optional[str] = None, 
                 abuse_threshold: float = 0.3,
                 nsfw_model: str = "nudenet",
                 whisper_model: str = "base") -> Dict[str, Any]:
    """
    Main video processing function with modern abuse classification.
    
    Args:
        input_path (str): Path to the input video file
        mode (str): Processing mode ('beep', 'mute', 'cut-scene', 'cut-nsfw')
        temp_dir (str, optional): Temporary directory for processing files
        abuse_threshold (float): Threshold for abuse detection (0.0-1.0)
        nsfw_model (str): Model type for NSFW detection
        whisper_model (str): Whisper model to use ('base', 'medium', 'large')
    
    Returns:
        Dict with processing results and output path
    
    Raises:
        Exception: If processing fails at any stage
    """
    try:
        # Validate inputs
        if not validate_video_file(input_path):
            raise Exception(f"Invalid or missing video file: {input_path}")
        
        if mode not in ['beep', 'mute', 'cut-scene', 'cut-nsfw']:
            raise Exception(f"Unsupported mode: {mode}. Use 'beep', 'mute', 'cut-scene', or 'cut-nsfw'")
        
        # Set up directories
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="profanity_filter_")
        
        temp_path = Path(temp_dir)
        temp_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique identifiers
        video_id = str(uuid.uuid4())
        input_filename = Path(input_path).stem
        
        print(f"🎥 Processing video: {input_filename}")
        print(f"📁 Using temp directory: {temp_dir}")
        print(f"🔧 Mode: {mode}")
        
        # Initialize results
        results = {
            'video_id': video_id,
            'input_path': input_path,
            'mode': mode,
            'temp_dir': temp_dir,
            'status': 'processing',
            'duration': 0,
            'abusive_segments': [],
            'nsfw_scenes': [],
            'output_path': None,
            'errors': []
        }
        
        # Get video duration
        duration = get_video_duration(input_path)
        results['duration'] = duration
        print(f"⏱️  Video duration: {duration:.2f} seconds")
        
        # Extract audio for transcription
        audio_path = temp_path / f"{video_id}_audio.wav"
        print("🎵 Extracting audio...")
        extract_audio(input_path, str(audio_path))
        
        # Transcribe audio using Whisper
        print(f"🎤 Transcribing audio with Whisper model: {whisper_model}")
        transcription_result = transcribe_with_whisper(str(audio_path), whisper_model)
        
        if not transcription_result or 'segments' not in transcription_result:
            raise Exception("Transcription failed or returned no segments")
        
        segments = transcription_result['segments']
        print(f"📝 Found {len(segments)} transcription segments")
        
        # Load abuse classifier
        print("🧠 Loading abuse classifier...")
        try:
            classifier = load_classifier()
            print(f"✅ Classifier loaded: {classifier.get_model_info()}")
        except Exception as e:
            print(f"⚠️  Could not load classifier: {e}")
            print("📦 Using fallback detection...")
            classifier = None
        
        # Detect abusive segments using the new classifier
        print("🔍 Detecting abusive words...")
        abusive_segments = detect_abusive_segments(segments, classifier, abuse_threshold)
        
        results['abusive_segments'] = abusive_segments
        print(f"🚨 Found {len(abusive_segments)} abusive words")
        
        # Handle different processing modes
        if mode == 'cut-nsfw':
            print("🔍 Detecting NSFW scenes...")
            nsfw_scenes = detect_nsfw_scenes(input_path, model_type=nsfw_model)
            results['nsfw_scenes'] = nsfw_scenes
            
            if nsfw_scenes:
                print(f"🚨 Found {len(nsfw_scenes)} NSFW scenes")
                output_path = temp_path / f"{input_filename}_nsfw_removed.mp4"
                cut_scenes(input_path, nsfw_scenes, str(output_path))
                results['output_path'] = str(output_path)
            else:
                print("✅ No NSFW content found")
                results['output_path'] = input_path
        
        elif abusive_segments:
            # Process abusive words
            print(f"🎛️  Applying {mode} to {len(abusive_segments)} abusive words...")
            
            if mode == 'beep':
                output_path = temp_path / f"{input_filename}_beeped.mp4"
                apply_beep_to_video(input_path, abusive_segments, str(output_path))
                
            elif mode == 'mute':
                output_path = temp_path / f"{input_filename}_muted.mp4"
                apply_mute_to_video(input_path, abusive_segments, str(output_path))
                
            elif mode == 'cut-scene':
                output_path = temp_path / f"{input_filename}_cut.mp4"
                cut_scenes(input_path, abusive_segments, str(output_path))
            
            results['output_path'] = str(output_path)
            print(f"✅ Processed video saved to: {output_path}")
            
        else:
            print("✅ No abusive words found")
            results['output_path'] = input_path
        
        results['status'] = 'completed'
        print("🎉 Video processing completed successfully")
        
        return results
        
    except Exception as e:
        error_msg = f"Video processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        if 'results' in locals():
            results['status'] = 'failed'
            results['errors'].append(error_msg)
            return results
        else:
            return {
                'status': 'failed',
                'error': error_msg,
                'input_path': input_path
            }


def detect_abusive_segments(segments: List[Dict[str, Any]], 
                          classifier, 
                          threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Detect abusive words (not entire segments) using word-level timestamps.
    
    Args:
        segments: List of transcription segments from Whisper
        classifier: The abuse classifier instance
        threshold: Confidence threshold for abuse detection
    
    Returns:
        List of abusive word segments with precise timestamps
    """
    abusive_segments = []
    
    if classifier is None:
        print("⚠️  No classifier available, using word-level fallback detection")
        return _fallback_word_level_detection(segments)
    
    try:
        for segment in segments:
            # Check if segment has word-level timestamps
            words = segment.get('words', [])
            if not words:
                # Fallback to segment-level if no word timestamps
                text = segment.get('text', '').strip()
                if text and classifier:
                    result = classifier.predict(text, return_score=True)
                    if _is_abusive_result(result, threshold):
                        abusive_segments.append({
                            'start': segment.get('start', 0),
                            'end': segment.get('end', 0),
                            'text': text,
                            'is_abusive': True,
                            'confidence': _get_confidence(result),
                            'method': 'segment_level'
                        })
                continue
            
            # Process each word individually
            for word_data in words:
                word_text = word_data.get('word', '').strip()
                if not word_text:
                    continue
                
                # Get prediction for individual word
                result = classifier.predict(word_text, return_score=True)
                
                if _is_abusive_result(result, threshold):
                    abusive_segments.append({
                        'start': word_data.get('start', 0),
                        'end': word_data.get('end', 0),
                        'text': word_text,
                        'is_abusive': True,
                        'confidence': _get_confidence(result),
                        'method': 'word_level'
                    })
    
    except Exception as e:
        print(f"❌ Classifier error: {e}")
        print("📦 Using word-level fallback detection...")
        return _fallback_word_level_detection(segments)
    
    # If classifier found nothing, also try fallback detection as a safety net
    if len(abusive_segments) == 0:
        print("📦 No classifier detections, trying word-level fallback detection...")
        fallback_segments = _fallback_word_level_detection(segments)
        if fallback_segments:
            print(f"✅ Fallback detected {len(fallback_segments)} abusive words")
            return fallback_segments
    
    return abusive_segments


def _is_abusive_result(result, threshold: float) -> bool:
    """Check if classifier result indicates abuse above threshold."""
    if isinstance(result, dict):
        is_abusive = result.get('is_abusive', False)
        confidence = result.get('confidence', 0.0)
        return is_abusive and confidence >= threshold
    return bool(result)


def _get_confidence(result) -> float:
    """Extract confidence score from classifier result."""
    if isinstance(result, dict):
        return result.get('confidence', 1.0)
    return 1.0


def _fallback_word_level_detection(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Word-level fallback abuse detection using keyword matching.
    """
    # Basic abuse words for fallback
    abuse_keywords = [
        'fuck', 'fucking', 'shit', 'damn', 'hell', 'ass', 'bitch', 'dick',
        'pussy', 'cock', 'bastard', 'crap', 'piss', 'whore', 'slut',
        'chutiya', 'madarchod', 'bc', 'behenchod', 'randi', 'saala',
        'bhosdi', 'lauda', 'lund', 'gandu', 'harami'
    ]
    
    abusive_segments = []
    
    for segment in segments:
        # Check if segment has word-level timestamps
        words = segment.get('words', [])
        if words:
            # Process individual words with timestamps
            for word_data in words:
                word_text = word_data.get('word', '').strip().lower()
                # Remove punctuation for comparison
                clean_word = ''.join(c for c in word_text if c.isalnum())
                
                if clean_word in abuse_keywords:
                    abusive_segments.append({
                        'start': word_data.get('start', 0),
                        'end': word_data.get('end', 0),
                        'text': word_data.get('word', ''),
                        'is_abusive': True,
                        'confidence': 1.0,
                        'method': 'word_level_fallback',
                        'detected_keyword': clean_word
                    })
        else:
            # Fallback to segment-level processing
            text = segment.get('text', '').strip().lower()
            if not text:
                continue
            
            # Check for abuse keywords in the segment
            text_words = text.split()
            for i, word in enumerate(text_words):
                clean_word = ''.join(c for c in word if c.isalnum())
                if clean_word in abuse_keywords:
                    # Estimate word timing within segment
                    segment_duration = segment.get('end', 0) - segment.get('start', 0)
                    word_duration = segment_duration / len(text_words)
                    word_start = segment.get('start', 0) + (i * word_duration)
                    word_end = word_start + word_duration
                    
                    abusive_segments.append({
                        'start': word_start,
                        'end': word_end,
                        'text': word,
                        'is_abusive': True,
                        'confidence': 1.0,
                        'method': 'segment_word_estimation',
                        'detected_keyword': clean_word
                    })
    
    return abusive_segments


def get_video_metadata(input_path: str) -> Dict[str, Any]:
    """
    Get metadata about a video file.
    
    Args:
        input_path: Path to the video file
        
    Returns:
        Dictionary with video metadata
    """
    try:
        if not validate_video_file(input_path):
            return {'error': 'Invalid video file'}
        
        duration = get_video_duration(input_path)
        file_size = os.path.getsize(input_path)
        
        return {
            'path': input_path,
            'duration': duration,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'valid': True
        }
        
    except Exception as e:
        return {
            'path': input_path,
            'error': str(e),
            'valid': False
        }


# For testing
if __name__ == "__main__":
    # Test with sample segments
    test_segments = [
        {'text': 'Hello everyone, welcome to the video', 'start': 0.0, 'end': 3.0},
        {'text': 'Tu chutiya hai yaar', 'start': 3.0, 'end': 6.0},
        {'text': 'This is good content', 'start': 6.0, 'end': 9.0},
        {'text': 'What the fuck is happening', 'start': 9.0, 'end': 12.0},
    ]
    
    print("🧪 Testing Modern Video Processor")
    print("=" * 50)
    
    # Test abuse detection
    try:
        classifier = load_classifier()
        print("✅ Classifier loaded successfully")
    except Exception as e:
        print(f"⚠️  Classifier not available: {e}")
        classifier = None
    
    abusive_segments = detect_abusive_segments(test_segments, classifier, threshold=0.5)
    
    print(f"\nFound {len(abusive_segments)} abusive segments:")
    for segment in abusive_segments:
        print(f"  🚨 [{segment['start']:.1f}s - {segment['end']:.1f}s]: \"{segment['text']}\"")
        print(f"     Confidence: {segment['confidence']:.3f}, Method: {segment['method']}")
    
    print("\n✅ Video processor ready for integration!")
