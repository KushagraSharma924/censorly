"""
Hybrid abuse detection combining transformer models and keyword matching.
Production-ready multilingual detection for Hindi, Hinglish, and English.
"""

import logging
import re
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import time
import threading

logger = logging.getLogger(__name__)

class HybridAbuseDetector:
    """
    Production-grade hybrid detector combining transformer and keyword detection.
    Optimized for multilingual abuse detection with fallback mechanisms.
    """
    
    def __init__(
        self,
        transformer_model_path: Optional[str] = None,
        use_transformer: bool = True,
        transformer_threshold: float = 0.7,
        keyword_confidence: float = 0.9,
        ensemble_mode: str = "hybrid"  # "hybrid", "transformer_first", "keyword_first"
    ):
        """
        Initialize hybrid detector.
        
        Args:
            transformer_model_path: Path to fine-tuned transformer model
            use_transformer: Whether to use transformer model
            transformer_threshold: Confidence threshold for transformer
            keyword_confidence: Fixed confidence for keyword matches
            ensemble_mode: How to combine predictions
        """
        self.use_transformer = use_transformer
        self.transformer_threshold = transformer_threshold
        self.keyword_confidence = keyword_confidence
        self.ensemble_mode = ensemble_mode
        
        # Initialize transformer
        self.transformer_classifier = None
        self.transformer_available = False
        
        if use_transformer:
            try:
                from .transformer_inference import TransformerAbuseDetector
                
                # Use specific model if provided, otherwise use IndicBERT
                if transformer_model_path and os.path.exists(transformer_model_path):
                    # Load custom fine-tuned model
                    logger.info(f"Loading custom transformer model from: {transformer_model_path}")
                    self.transformer_classifier = TransformerAbuseDetector(
                        model_name=transformer_model_path,
                        confidence_threshold=transformer_threshold
                    )
                else:
                    # Use pre-trained IndicBERT for multilingual support
                    logger.info("Loading pre-trained IndicBERT model for multilingual detection")
                    self.transformer_classifier = TransformerAbuseDetector(
                        model_name="ai4bharat/indic-bert",
                        confidence_threshold=transformer_threshold
                    )
                
                # Test load to verify it works
                if self.transformer_classifier.load_model():
                    self.transformer_available = True
                    logger.info("✅ Transformer model loaded successfully")
                else:
                    logger.warning("❌ Failed to load transformer model, using keyword-only mode")
                    self.transformer_classifier = None
                    
            except ImportError as e:
                logger.error(f"❌ Transformer dependencies not available: {e}")
                logger.info("   Falling back to keyword-only mode")
            except Exception as e:
                logger.error(f"❌ Transformer initialization failed: {e}")
                logger.info("   Falling back to keyword-only detection")
        
        # Initialize keyword detector
        self.keyword_detector = KeywordAbuseDetector()
        
        # Performance tracking
        self.stats = {
            'total_predictions': 0,
            'transformer_predictions': 0,
            'keyword_predictions': 0,
            'hybrid_agreements': 0,
            'hybrid_disagreements': 0,
            'avg_transformer_time': 0.0,
            'avg_keyword_time': 0.0,
            'avg_total_time': 0.0,
            'cache_hits': 0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info(f"Hybrid detector initialized - Mode: {ensemble_mode}")
        logger.info(f"Transformer available: {self.transformer_available}")
    
    def predict(self, text: str, return_score: bool = True) -> Dict[str, Any]:
        """
        Make hybrid prediction combining transformer and keyword detection.
        
        Args:
            text: Input text
            return_score: Whether to return detailed scores
            
        Returns:
            Combined prediction result
        """
        if not text or not text.strip():
            return {
                'text': text,
                'is_abusive': False,
                'confidence': 0.0,
                'method': 'none'
            }
        
        start_time = time.time()
        text = text.strip()
        
        with self._lock:
            self.stats['total_predictions'] += 1
        
        # Get predictions from available methods
        transformer_result = None
        keyword_result = None
        
        if self.transformer_available:
            transformer_result = self._predict_transformer(text)
            
        keyword_result = self._predict_keyword(text)
        
        # Combine results based on ensemble mode
        final_result = self._combine_predictions(
            transformer_result, 
            keyword_result, 
            text
        )
        
        # Add timing info
        total_time = (time.time() - start_time) * 1000
        final_result['total_inference_time_ms'] = total_time
        
        with self._lock:
            self.stats['avg_total_time'] = (
                (self.stats['avg_total_time'] * (self.stats['total_predictions'] - 1) + total_time) / 
                self.stats['total_predictions']
            )
        
        # Format response
        response = {
            'text': text,
            'is_abusive': final_result['is_abusive'],
            'confidence': final_result['confidence'],
            'method': final_result['method']
        }
        
        if return_score:
            response.update({
                'transformer_result': transformer_result,
                'keyword_result': keyword_result,
                'detected_words': final_result.get('detected_words', []),
                'total_inference_time_ms': total_time,
                'model_info': self.get_model_info()
            })
        
        return response
    
    def _predict_transformer(self, text: str) -> Optional[Dict[str, Any]]:
        """Get transformer prediction"""
        if not self.transformer_available or not self.transformer_classifier:
            return None
        
        try:
            start_time = time.time()
            result = self.transformer_classifier.predict(text, return_score=True)
            
            inference_time = (time.time() - start_time) * 1000
            
            with self._lock:
                self.stats['transformer_predictions'] += 1
                self.stats['avg_transformer_time'] = (
                    (self.stats['avg_transformer_time'] * (self.stats['transformer_predictions'] - 1) + inference_time) / 
                    self.stats['transformer_predictions']
                )
            
            return {
                'is_abusive': result['is_abusive'],
                'confidence': result['confidence'],
                'method': 'transformer',
                'inference_time_ms': inference_time,
                'model_path': result.get('model_info', {}).get('model_path', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Transformer prediction failed: {e}")
            return None
    
    def _predict_keyword(self, text: str) -> Dict[str, Any]:
        """Get keyword-based prediction"""
        try:
            start_time = time.time()
            result = self.keyword_detector.detect(text)
            
            inference_time = (time.time() - start_time) * 1000
            
            with self._lock:
                self.stats['keyword_predictions'] += 1
                self.stats['avg_keyword_time'] = (
                    (self.stats['avg_keyword_time'] * (self.stats['keyword_predictions'] - 1) + inference_time) / 
                    self.stats['keyword_predictions']
                )
            
            return {
                'is_abusive': result['is_abusive'],
                'confidence': self.keyword_confidence if result['is_abusive'] else 0.0,
                'detected_words': result['detected_words'],
                'method': 'keyword',
                'inference_time_ms': inference_time
            }
            
        except Exception as e:
            logger.error(f"Keyword prediction failed: {e}")
            return {
                'is_abusive': False,
                'confidence': 0.0,
                'detected_words': [],
                'method': 'keyword',
                'error': str(e)
            }
    
    def _combine_predictions(
        self, 
        transformer_result: Optional[Dict[str, Any]], 
        keyword_result: Dict[str, Any],
        text: str
    ) -> Dict[str, Any]:
        """Combine transformer and keyword predictions"""
        
        # If only keyword detection available
        if not transformer_result:
            return {
                'is_abusive': keyword_result['is_abusive'],
                'confidence': keyword_result['confidence'],
                'detected_words': keyword_result.get('detected_words', []),
                'method': 'keyword_only'
            }
        
        # Both methods available - combine based on ensemble mode
        transformer_abusive = transformer_result['is_abusive']
        transformer_conf = transformer_result['confidence']
        keyword_abusive = keyword_result['is_abusive']
        keyword_conf = keyword_result['confidence']
        
        if self.ensemble_mode == "transformer_first":
            # Trust transformer if confident, fallback to keyword
            if transformer_conf >= self.transformer_threshold:
                return {
                    'is_abusive': transformer_abusive,
                    'confidence': transformer_conf,
                    'detected_words': keyword_result.get('detected_words', []),
                    'method': 'transformer_primary'
                }
            else:
                return {
                    'is_abusive': keyword_abusive,
                    'confidence': keyword_conf,
                    'detected_words': keyword_result.get('detected_words', []),
                    'method': 'keyword_fallback'
                }
        
        elif self.ensemble_mode == "keyword_first":
            # Use keyword detection first, transformer for verification
            if keyword_abusive:
                return {
                    'is_abusive': True,
                    'confidence': max(keyword_conf, transformer_conf),
                    'detected_words': keyword_result.get('detected_words', []),
                    'method': 'keyword_primary'
                }
            else:
                return {
                    'is_abusive': transformer_abusive,
                    'confidence': transformer_conf,
                    'detected_words': keyword_result.get('detected_words', []),
                    'method': 'transformer_secondary'
                }
        
        else:  # "hybrid" mode - intelligent combination
            # If both agree, use higher confidence
            if transformer_abusive == keyword_abusive:
                with self._lock:
                    self.stats['hybrid_agreements'] += 1
                
                return {
                    'is_abusive': transformer_abusive,
                    'confidence': max(transformer_conf, keyword_conf),
                    'detected_words': keyword_result.get('detected_words', []),
                    'method': 'hybrid_agreement'
                }
            
            # If they disagree, use the one with higher confidence
            else:
                with self._lock:
                    self.stats['hybrid_disagreements'] += 1
                
                if transformer_conf > keyword_conf:
                    return {
                        'is_abusive': transformer_abusive,
                        'confidence': transformer_conf,
                        'detected_words': keyword_result.get('detected_words', []),
                        'method': 'hybrid_transformer_wins'
                    }
                else:
                    return {
                        'is_abusive': keyword_abusive,
                        'confidence': keyword_conf,
                        'detected_words': keyword_result.get('detected_words', []),
                        'method': 'hybrid_keyword_wins'
                    }
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Batch prediction for multiple texts"""
        results = []
        
        # Use transformer batch processing if available
        if self.transformer_available and self.transformer_classifier:
            try:
                transformer_results = self.transformer_classifier.predict_batch(texts)
                keyword_results = [self.keyword_detector.detect(text) for text in texts]
                
                for i, text in enumerate(texts):
                    transformer_result = transformer_results[i]
                    keyword_result = keyword_results[i]
                    
                    # Convert to expected format
                    transformer_formatted = {
                        'is_abusive': transformer_result['is_abusive'],
                        'confidence': transformer_result['confidence'],
                        'method': 'transformer'
                    }
                    
                    keyword_formatted = {
                        'is_abusive': keyword_result['is_abusive'],
                        'confidence': self.keyword_confidence if keyword_result['is_abusive'] else 0.0,
                        'detected_words': keyword_result['detected_words'],
                        'method': 'keyword'
                    }
                    
                    combined = self._combine_predictions(transformer_formatted, keyword_formatted, text)
                    combined['text'] = text
                    results.append(combined)
                
                return results
                
            except Exception as e:
                logger.error(f"Batch prediction failed: {e}")
        
        # Fallback to individual predictions
        return [self.predict(text, return_score=False) for text in texts]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        info = {
            'ensemble_mode': self.ensemble_mode,
            'transformer_available': self.transformer_available,
            'transformer_threshold': self.transformer_threshold,
            'keyword_confidence': self.keyword_confidence
        }
        
        if self.transformer_available and self.transformer_classifier:
            info['transformer_info'] = self.transformer_classifier.get_model_info()
        
        return info
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.stats.copy()
        
        if self.transformer_available and self.transformer_classifier:
            transformer_info = self.transformer_classifier.get_model_info()
            stats['transformer_info'] = transformer_info
        
        return stats
    
    def set_threshold(self, threshold: float):
        """Update transformer threshold"""
        self.transformer_threshold = threshold
        if self.transformer_available and self.transformer_classifier:
            # Update the confidence threshold directly on the transformer
            self.transformer_classifier.confidence_threshold = threshold
        logger.info(f"Threshold updated to {threshold}")


class KeywordAbuseDetector:
    """
    Enhanced keyword-based abuse detector for multilingual content.
    Supports English, Hindi, and Hinglish with advanced pattern matching.
    """
    
    def __init__(self):
        # English abuse words
        self.english_words = {
            'fuck', 'fucking', 'fucked', 'fucker', 'fuk', 'fck', 'f*ck',
            'shit', 'bullshit', 'horseshit',
            'bitch', 'bitches', 'son of a bitch', 'b*tch',
            'asshole', 'ass', 'dumbass', 'jackass',
            'damn', 'goddamn', 'dammit',
            'hell', 'go to hell',
            'bastard', 'bastards',
            'crap', 'crappy',
            'piss', 'pissed', 'piss off',
            'whore', 'slut', 'sluts',
            'dick', 'dickhead',
            'pussy', 'cock', 'penis',
            'stupid', 'idiot', 'moron', 'retard'
        }
        
        # Hindi abuse words
        self.hindi_words = {
            'चूतिया', 'मादरचोद', 'भेनचोद', 'भोसड़ी', 'रंडी', 'साला', 'कुत्ता',
            'हरामी', 'गांडू', 'लौड़ा', 'लंड', 'भोसड़ा', 'रंड', 'कमीना'
        }
        
        # Hinglish/Romanized Hindi abuse words  
        self.hinglish_words = {
            'chutiya', 'chutiye', 'madarchod', 'mc', 'behenchod', 'bc',
            'bhosdi', 'bhosda', 'randi', 'saala', 'sala', 'kutta',
            'harami', 'gandu', 'lauda', 'lund', 'kamina', 'kameena',
            'bhenchod', 'madarchod', 'maderchod', 'benchod', 'bhencho',
            'chodu', 'chomu', 'gaandu', 'gand', 'rand'
        }
        
        # Combine all wordlists
        self.all_words = self.english_words | self.hindi_words | self.hinglish_words
        
        # Common obfuscation patterns
        self.obfuscation_map = {
            '@': 'a', '$': 's', '3': 'e', '1': 'i', '0': 'o',
            '4': 'a', '5': 's', '7': 't', '8': 'b', '!': 'i',
            '*': '', '#': '', '%': '', '&': 'and'
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        text = text.lower().strip()
        
        # Handle obfuscation
        for char, replacement in self.obfuscation_map.items():
            text = text.replace(char, replacement)
        
        # Remove extra spaces and punctuation
        import re
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect abuse using keyword matching with proper word boundaries.
        
        Args:
            text: Input text
            
        Returns:
            Detection result with detected words
        """
        if not text or not text.strip():
            return {
                'is_abusive': False,
                'detected_words': [],
                'confidence': 0.0
            }
        
        normalized_text = self._normalize_text(text)
        detected_words = []
        
        # Check for exact word matches using word boundaries
        for abuse_word in self.all_words:
            # Create regex pattern for word boundaries
            pattern = r'\b' + re.escape(abuse_word) + r'\b'
            if re.search(pattern, normalized_text, re.IGNORECASE):
                detected_words.append(abuse_word)
        
        # Check for obfuscated words (only for longer words to avoid false positives)
        for abuse_word in self.all_words:
            if len(abuse_word) > 4:  # Only check longer words for obfuscation
                # Look for obfuscated versions with character substitutions
                obfuscated_pattern = self._create_obfuscated_pattern(abuse_word)
                if re.search(obfuscated_pattern, normalized_text, re.IGNORECASE):
                    if abuse_word not in detected_words:
                        detected_words.append(abuse_word)
        
        is_abusive = len(detected_words) > 0
        confidence = 0.9 if is_abusive else 0.1
        
        return {
            'is_abusive': is_abusive,
            'detected_words': detected_words,
            'confidence': confidence
        }
    
    def _create_obfuscated_pattern(self, word: str) -> str:
        """
        Create regex pattern to match obfuscated versions of a word.
        
        Args:
            word: Original abuse word
            
        Returns:
            Regex pattern for obfuscated matches
        """
        # Convert word to pattern that handles common obfuscations
        pattern = r'\b'
        for char in word:
            if char in self.obfuscation_map:
                # Create character class for obfuscated characters
                obf_chars = ''.join(self.obfuscation_map[char])
                pattern += f'[{re.escape(char)}{re.escape(obf_chars)}]'
            else:
                pattern += re.escape(char)
        pattern += r'\b'
        return pattern
        
        return {
            'is_abusive': len(detected_words) > 0,
            'detected_words': detected_words,
            'confidence': 1.0 if detected_words else 0.0
        }


# Legacy compatibility - keep the old class name
HybridProfanityDetector = HybridAbuseDetector
