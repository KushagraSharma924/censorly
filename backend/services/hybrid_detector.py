"""
Hybrid profanity detection combining regex patterns and transformer models.
Provides fallback mechanism and ensemble predictions for production use.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class HybridProfanityDetector:
    """
    Hybrid detector that combines regex-based and transformer-based approaches.
    Provides fast regex detection with transformer verification for accuracy.
    """
    
    def __init__(
        self,
        transformer_model_path: Optional[str] = None,
        use_transformer: bool = True,
        transformer_threshold: float = 0.7,
        ensemble_mode: str = "fast_first"  # "fast_first", "both", "transformer_only"
    ):
        """
        Initialize hybrid detector.
        
        Args:
            transformer_model_path: Path to transformer model
            use_transformer: Whether to use transformer model
            transformer_threshold: Confidence threshold for transformer
            ensemble_mode: How to combine predictions
                - "fast_first": Use regex first, transformer for verification
                - "both": Use both and combine results
                - "transformer_only": Use only transformer
        """
        self.use_transformer = use_transformer
        self.transformer_threshold = transformer_threshold
        self.ensemble_mode = ensemble_mode
        
        # Initialize regex scanner
        try:
            from .profanity_scanner import get_scanner
            self.regex_scanner = get_scanner()
            self.regex_available = True
            logger.info("✅ Regex scanner initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize regex scanner: {e}")
            self.regex_scanner = None
            self.regex_available = False
        
        # Initialize transformer classifier
        self.transformer_classifier = None
        self.transformer_available = False
        
        if use_transformer and transformer_model_path:
            try:
                from .transformer_classifier import TransformerInference
                self.transformer_classifier = TransformerInference(
                    transformer_model_path, 
                    transformer_threshold
                )
                self.transformer_available = True
                logger.info("✅ Transformer classifier initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize transformer: {e}")
                logger.info("   Falling back to regex-only mode")
        
        # Performance tracking
        self.stats = {
            'total_predictions': 0,
            'regex_predictions': 0,
            'transformer_predictions': 0,
            'hybrid_agreements': 0,
            'hybrid_disagreements': 0,
            'avg_regex_time': 0.0,
            'avg_transformer_time': 0.0,
            'avg_total_time': 0.0
        }
        
        logger.info(f"Hybrid detector initialized - Mode: {ensemble_mode}")
        logger.info(f"Available methods: Regex={self.regex_available}, Transformer={self.transformer_available}")
    
    def _predict_regex(self, text: str) -> Dict[str, Any]:
        """Get regex-based prediction."""
        if not self.regex_available:
            return {'is_abusive': False, 'confidence': 0.0, 'method': 'regex', 'words': []}
        
        start_time = time.time()
        
        try:
            is_abusive = self.regex_scanner.is_abusive(text)
            matches = self.regex_scanner.find_profanity_matches(text)
            words = [match['word'] for match in matches]
            
            # Confidence based on number of matches
            confidence = min(1.0, len(words) * 0.5 + 0.5) if is_abusive else 0.0
            
            inference_time = (time.time() - start_time) * 1000
            
            return {
                'is_abusive': is_abusive,
                'confidence': confidence,
                'words': words,
                'matches': matches,
                'method': 'regex',
                'inference_time_ms': inference_time
            }
            
        except Exception as e:
            logger.error(f"Regex prediction failed: {e}")
            return {'is_abusive': False, 'confidence': 0.0, 'method': 'regex', 'words': []}
    
    def _predict_transformer(self, text: str) -> Dict[str, Any]:
        """Get transformer-based prediction."""
        if not self.transformer_available:
            return {'is_abusive': False, 'confidence': 0.0, 'method': 'transformer'}
        
        try:
            result = self.transformer_classifier.predict(text)
            return {
                'is_abusive': result['is_abusive'],
                'confidence': result['confidence'],
                'label': result['label'],
                'method': 'transformer',
                'inference_time_ms': result['inference_time_ms'],
                'normalized_text': result.get('normalized_text', text)
            }
            
        except Exception as e:
            logger.error(f"Transformer prediction failed: {e}")
            return {'is_abusive': False, 'confidence': 0.0, 'method': 'transformer'}
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Make hybrid prediction.
        
        Args:
            text: Input text
            
        Returns:
            Combined prediction result
        """
        if not text or not text.strip():
            return {
                'text': text,
                'is_abusive': False,
                'confidence': 0.0,
                'method': 'none',
                'predictions': {}
            }
        
        start_time = time.time()
        predictions = {}
        
        # Update stats
        self.stats['total_predictions'] += 1
        
        if self.ensemble_mode == "transformer_only":
            # Use only transformer
            transformer_result = self._predict_transformer(text)
            predictions['transformer'] = transformer_result
            
            final_result = {
                'text': text,
                'is_abusive': transformer_result['is_abusive'],
                'confidence': transformer_result['confidence'],
                'method': 'transformer_only',
                'predictions': predictions
            }
            
        elif self.ensemble_mode == "fast_first":
            # Use regex first, transformer for verification if needed
            regex_result = self._predict_regex(text)
            predictions['regex'] = regex_result
            self.stats['regex_predictions'] += 1
            
            if regex_result['is_abusive']:
                # Regex detected abuse, verify with transformer if available
                if self.transformer_available:
                    transformer_result = self._predict_transformer(text)
                    predictions['transformer'] = transformer_result
                    self.stats['transformer_predictions'] += 1
                    
                    # Combine results - both must agree for high confidence
                    if transformer_result['is_abusive']:
                        # Both agree on abusive
                        final_is_abusive = True
                        final_confidence = min(1.0, (regex_result['confidence'] + transformer_result['confidence']) / 2)
                        self.stats['hybrid_agreements'] += 1
                    else:
                        # Disagreement - use transformer with lower confidence
                        final_is_abusive = transformer_result['is_abusive']
                        final_confidence = transformer_result['confidence'] * 0.8  # Penalty for disagreement
                        self.stats['hybrid_disagreements'] += 1
                else:
                    # No transformer, use regex result
                    final_is_abusive = regex_result['is_abusive']
                    final_confidence = regex_result['confidence']
            else:
                # Regex says clean, trust it (fast path)
                final_is_abusive = False
                final_confidence = 0.0
            
            final_result = {
                'text': text,
                'is_abusive': final_is_abusive,
                'confidence': final_confidence,
                'method': 'fast_first',
                'predictions': predictions
            }
            
        elif self.ensemble_mode == "both":
            # Use both methods and combine
            regex_result = self._predict_regex(text)
            transformer_result = self._predict_transformer(text)
            
            predictions['regex'] = regex_result
            predictions['transformer'] = transformer_result
            
            self.stats['regex_predictions'] += 1
            if self.transformer_available:
                self.stats['transformer_predictions'] += 1
            
            # Ensemble logic
            if regex_result['is_abusive'] and transformer_result['is_abusive']:
                # Both say abusive - high confidence
                final_is_abusive = True
                final_confidence = max(regex_result['confidence'], transformer_result['confidence'])
                self.stats['hybrid_agreements'] += 1
            elif regex_result['is_abusive'] or transformer_result['is_abusive']:
                # One says abusive - medium confidence
                final_is_abusive = True
                final_confidence = max(regex_result['confidence'], transformer_result['confidence']) * 0.7
                self.stats['hybrid_disagreements'] += 1
            else:
                # Both say clean
                final_is_abusive = False
                final_confidence = 0.0
                self.stats['hybrid_agreements'] += 1
            
            final_result = {
                'text': text,
                'is_abusive': final_is_abusive,
                'confidence': final_confidence,
                'method': 'both',
                'predictions': predictions
            }
        
        else:
            raise ValueError(f"Unknown ensemble_mode: {self.ensemble_mode}")
        
        # Add timing info
        total_time = (time.time() - start_time) * 1000
        final_result['total_inference_time_ms'] = total_time
        
        # Update timing stats
        self._update_timing_stats(predictions, total_time)
        
        return final_result
    
    def _update_timing_stats(self, predictions: Dict[str, Any], total_time: float):
        """Update timing statistics."""
        if 'regex' in predictions:
            regex_time = predictions['regex'].get('inference_time_ms', 0)
            self._update_avg('avg_regex_time', regex_time, self.stats['regex_predictions'])
        
        if 'transformer' in predictions:
            transformer_time = predictions['transformer'].get('inference_time_ms', 0)
            self._update_avg('avg_transformer_time', transformer_time, self.stats['transformer_predictions'])
        
        self._update_avg('avg_total_time', total_time, self.stats['total_predictions'])
    
    def _update_avg(self, stat_name: str, new_value: float, count: int):
        """Update running average."""
        if count <= 1:
            self.stats[stat_name] = new_value
        else:
            current_avg = self.stats[stat_name]
            self.stats[stat_name] = (current_avg * (count - 1) + new_value) / count
    
    def predict_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict abusive segments with hybrid approach.
        
        Args:
            segments: Whisper segments
            
        Returns:
            List of abusive segments
        """
        abusive_segments = []
        
        for segment in segments:
            text = segment.get('text', '').strip()
            if not text:
                continue
            
            prediction = self.predict(text)
            
            if prediction['is_abusive']:
                abusive_segment = {
                    'text': text,
                    'start': segment.get('start', 0.0),
                    'end': segment.get('end', 0.0),
                    'confidence': prediction['confidence'],
                    'method': prediction['method'],
                    'predictions': prediction['predictions'],
                    'inference_time_ms': prediction['total_inference_time_ms']
                }
                
                # Add detected words if available
                if 'regex' in prediction['predictions']:
                    abusive_segment['profane_words'] = prediction['predictions']['regex'].get('words', [])
                
                abusive_segments.append(abusive_segment)
        
        logger.info(f"Hybrid detector found {len(abusive_segments)} abusive segments out of {len(segments)} total")
        
        return abusive_segments
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        stats = self.stats.copy()
        
        # Add agreement ratio
        total_hybrid = self.stats['hybrid_agreements'] + self.stats['hybrid_disagreements']
        if total_hybrid > 0:
            stats['agreement_ratio'] = self.stats['hybrid_agreements'] / total_hybrid
        else:
            stats['agreement_ratio'] = 1.0
        
        stats.update({
            'ensemble_mode': self.ensemble_mode,
            'regex_available': self.regex_available,
            'transformer_available': self.transformer_available,
            'use_transformer': self.use_transformer
        })
        
        return stats
    
    def benchmark(self, test_texts: List[str]) -> Dict[str, Any]:
        """
        Benchmark the hybrid detector.
        
        Args:
            test_texts: List of texts to benchmark
            
        Returns:
            Benchmark results
        """
        start_time = time.time()
        results = []
        
        for text in test_texts:
            result = self.predict(text)
            results.append(result)
        
        total_time = time.time() - start_time
        avg_time_ms = (total_time / len(test_texts)) * 1000
        
        # Count predictions by method
        method_counts = {}
        abusive_count = 0
        
        for result in results:
            method = result['method']
            method_counts[method] = method_counts.get(method, 0) + 1
            if result['is_abusive']:
                abusive_count += 1
        
        benchmark_results = {
            'total_texts': len(test_texts),
            'total_time_s': total_time,
            'avg_time_ms': avg_time_ms,
            'abusive_detected': abusive_count,
            'abusive_ratio': abusive_count / len(test_texts),
            'method_distribution': method_counts,
            'stats': self.get_stats()
        }
        
        return benchmark_results

# Global hybrid detector instance
_global_hybrid_detector: Optional[HybridProfanityDetector] = None

def get_hybrid_detector(
    transformer_model_path: Optional[str] = None,
    ensemble_mode: str = "fast_first"
) -> HybridProfanityDetector:
    """
    Get global hybrid detector instance.
    
    Args:
        transformer_model_path: Path to transformer model
        ensemble_mode: Ensemble mode
        
    Returns:
        HybridProfanityDetector instance
    """
    global _global_hybrid_detector
    
    if _global_hybrid_detector is None:
        _global_hybrid_detector = HybridProfanityDetector(
            transformer_model_path=transformer_model_path,
            ensemble_mode=ensemble_mode
        )
    
    return _global_hybrid_detector

def detect_abusive_hybrid(text: str) -> bool:
    """
    Simple function to detect abusive text using hybrid approach.
    
    Args:
        text: Input text
        
    Returns:
        True if abusive, False otherwise
    """
    detector = get_hybrid_detector()
    result = detector.predict(text)
    return result['is_abusive']

def detect_abusive_segments_hybrid(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect abusive segments using hybrid approach.
    
    Args:
        segments: Whisper segments
        
    Returns:
        List of abusive segments
    """
    detector = get_hybrid_detector()
    return detector.predict_segments(segments)
