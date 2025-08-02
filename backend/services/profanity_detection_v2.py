"""
Enhanced Profanity Detection Module - V2
Integrates hybrid detection combining regex-based and ML-based approaches.
"""

from typing import Dict, List, Any, Optional
import time
import logging
from services.hybrid_detector import HybridProfanityDetector

logger = logging.getLogger(__name__)

# Global hybrid detector instance
_hybrid_detector = None

def get_hybrid_detector() -> HybridProfanityDetector:
    """Get or initialize the global hybrid detector."""
    global _hybrid_detector
    if _hybrid_detector is None:
        _hybrid_detector = HybridProfanityDetector(
            transformer_model_path="./models/abusive_classifier_indic/production",
            ensemble_mode="fast_first"  # Fast for production
        )
    return _hybrid_detector

def detect_abusive_words_v2(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Enhanced detection using hybrid approach (regex + ML).
    
    Args:
        transcript_data: Dictionary containing 'segments' key with transcription segments
        
    Returns:
        List of detected abusive segments with enhanced metadata
    """
    if not transcript_data or 'segments' not in transcript_data:
        return []
    
    try:
        # Initialize hybrid detector
        detector = get_hybrid_detector()
        
        # Extract segments
        segments = transcript_data.get('segments', [])
        if not segments:
            return []
        
        # Detect abusive segments using hybrid approach
        abusive_segments = detector.predict_segments(segments)
        
        # Convert to expected format for backward compatibility
        result_segments = []
        for segment in abusive_segments:
            result_segments.append({
                'text': segment['text'],
                'start': segment['start'],
                'end': segment['end'],
                'confidence': segment['confidence'],
                'method': segment['method'],  # 'regex', 'transformer', or 'fast_first'
                'profane_words': segment.get('profane_words', []),
                'inference_time_ms': segment.get('inference_time_ms', 0),
                'severity': _get_severity_level(segment['confidence'])
            })
        
        logger.info(f"Detected {len(result_segments)} abusive segments using hybrid approach")
        return result_segments
        
    except Exception as e:
        logger.error(f"Error in hybrid profanity detection: {e}")
        # Fallback to original detection method
        return detect_abusive_words_fallback(transcript_data)

def detect_abusive_words_fallback(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fallback detection using original regex-only approach.
    """
    if not transcript_data or 'segments' not in transcript_data:
        return []
    
    try:
        from services.profanity_scanner import get_scanner
        scanner = get_scanner()
        
        segments = transcript_data.get('segments', [])
        abusive_segments = []
        
        for segment in segments:
            text = segment.get('text', '')
            if scanner.is_abusive(text):
                abusive_segments.append({
                    'text': text,
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'confidence': 1.0,  # High confidence for regex matches
                    'method': 'regex_fallback',
                    'profane_words': [],
                    'inference_time_ms': 0,
                    'severity': 'high'
                })
        
        return abusive_segments
        
    except Exception as e:
        logger.error(f"Error in fallback profanity detection: {e}")
        return []

def _get_severity_level(confidence: float) -> str:
    """
    Determine severity level based on confidence score.
    
    Args:
        confidence: Confidence score (0-1)
        
    Returns:
        Severity level: 'low', 'medium', or 'high'
    """
    if confidence >= 0.8:
        return 'high'
    elif confidence >= 0.5:
        return 'medium'
    else:
        return 'low'

def detect_abusive_segments_hybrid(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Direct segment detection for Celery worker integration.
    
    Args:
        segments: List of segments with 'text', 'start', 'end' keys
        
    Returns:
        List of abusive segments
    """
    try:
        detector = get_hybrid_detector()
        return detector.predict_segments(segments)
    except Exception as e:
        logger.error(f"Error in hybrid segment detection: {e}")
        # Fallback to regex-only
        from services.profanity_scanner import get_scanner
        scanner = get_scanner()
        
        abusive_segments = []
        for segment in segments:
            text = segment.get('text', '')
            if scanner.is_abusive(text):
                abusive_segments.append({
                    'text': text,
                    'start': segment.get('start', 0),
                    'end': segment.get('end', 0),
                    'confidence': 1.0,
                    'method': 'regex_fallback',
                    'profane_words': [],
                    'inference_time_ms': 0
                })
        
        return abusive_segments

def get_detection_stats() -> Dict[str, Any]:
    """
    Get statistics from the hybrid detector.
    
    Returns:
        Dictionary with detection statistics
    """
    try:
        detector = get_hybrid_detector()
        return detector.get_stats()
    except Exception as e:
        logger.error(f"Error getting detection stats: {e}")
        return {
            'total_predictions': 0,
            'error': str(e)
        }

def benchmark_detection_methods(test_texts: List[str]) -> Dict[str, Any]:
    """
    Benchmark different detection methods for comparison.
    
    Args:
        test_texts: List of texts to test
        
    Returns:
        Benchmark results comparing methods
    """
    try:
        detector = get_hybrid_detector()
        return detector.benchmark(test_texts)
    except Exception as e:
        logger.error(f"Error in benchmark: {e}")
        return {
            'error': str(e)
        }

# Backward compatibility - alias the original function name
detect_abusive_words = detect_abusive_words_v2

if __name__ == "__main__":
    # Test the enhanced detection
    test_transcript = {
        'segments': [
            {'text': 'Hello how are you today', 'start': 0.0, 'end': 2.5},
            {'text': 'Tu chutiya hai yaar', 'start': 2.5, 'end': 5.0},
            {'text': 'What the hell is this', 'start': 5.0, 'end': 7.5},
            {'text': 'BC madarchod saala', 'start': 7.5, 'end': 10.0},
            {'text': 'Thank you so much', 'start': 10.0, 'end': 12.5}
        ]
    }
    
    print("🧪 Testing Enhanced Profanity Detection V2")
    print("=" * 50)
    
    start_time = time.time()
    abusive_segments = detect_abusive_words_v2(test_transcript)
    end_time = time.time()
    
    print(f"Detected {len(abusive_segments)} abusive segments in {(end_time - start_time)*1000:.1f}ms:")
    
    for segment in abusive_segments:
        print(f"  🔴 [{segment['start']:.1f}-{segment['end']:.1f}s] '{segment['text']}'")
        print(f"     Method: {segment['method']}, Confidence: {segment['confidence']:.3f}")
        print(f"     Severity: {segment['severity']}, Time: {segment['inference_time_ms']:.1f}ms")
    
    # Get stats
    stats = get_detection_stats()
    print(f"\n📊 Detection Statistics:")
    print(f"   Total predictions: {stats.get('total_predictions', 0)}")
    print(f"   Average regex time: {stats.get('avg_regex_time', 0):.2f}ms")
    print(f"   Average transformer time: {stats.get('avg_transformer_time', 0):.2f}ms")
