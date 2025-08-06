"""
Production inference wrapper for fine-tuned transformer models.
Optimized for fast inference in Flask backend with caching and normalization.
"""

import os
import json
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import threading
from functools import lru_cache

import torch
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

from .transformer_trainer import TextNormalizer

logger = logging.getLogger(__name__)

class TransformerInference:
    """
    Production-ready inference wrapper for transformer-based abusive language detection.
    Optimized for sub-100ms inference with caching and batch processing.
    """
    
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.7,
        cache_size: int = 1000,
        max_length: int = 128
    ):
        """
        Initialize the inference wrapper.
        
        Args:
            model_path: Path to the fine-tuned model
            confidence_threshold: Minimum confidence for abusive classification
            cache_size: Size of LRU cache for repeated texts
            max_length: Maximum sequence length
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.cache_size = cache_size
        self.max_length = max_length
        
        # Initialize components
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        self.normalizer = TextNormalizer()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Performance tracking
        self.inference_stats = {
            'total_predictions': 0,
            'cache_hits': 0,
            'avg_inference_time': 0.0,
            'last_updated': time.time()
        }
        
        # Thread lock for thread safety
        self._lock = threading.Lock()
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the fine-tuned model and create pipeline."""
        try:
            logger.info(f"Loading model from: {self.model_path}")
            
            # Load configuration if available
            config_path = self.model_path / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Model config: {config}")
            
            # Create pipeline with optimization
            self.pipeline = pipeline(
                "text-classification",
                model=str(self.model_path),
                tokenizer=str(self.model_path),
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True,
                framework="pt"
            )
            
            # Load tokenizer separately for manual tokenization if needed
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            
            logger.info(f"Model loaded successfully on device: {self.device}")
            
            # Warm up the model
            self._warmup()
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _warmup(self):
        """Warm up the model with sample predictions."""
        warmup_texts = [
            "Hello world",
            "Test message",
            "Quick prediction"
        ]
        
        logger.info("Warming up model...")
        for text in warmup_texts:
            self._predict_single(text)
        logger.info("Model warmup completed")
    
    @lru_cache(maxsize=1000)
    def _cached_predict(self, normalized_text: str) -> Tuple[str, float]:
        """
        Cached prediction for normalized text.
        
        Args:
            normalized_text: Pre-normalized text
            
        Returns:
            Tuple of (label, confidence)
        """
        with self._lock:
            self.inference_stats['cache_hits'] += 1
        
        return self._predict_single(normalized_text, skip_normalization=True)
    
    def _predict_single(self, text: str, skip_normalization: bool = False) -> Tuple[str, float]:
        """
        Make a single prediction.
        
        Args:
            text: Input text
            skip_normalization: Whether to skip text normalization
            
        Returns:
            Tuple of (label, confidence)
        """
        if not skip_normalization:
            text = self.normalizer.normalize_text(text)
        
        start_time = time.time()
        
        try:
            # Make prediction
            results = self.pipeline(text)
            
            # Extract best prediction
            best_result = max(results, key=lambda x: x['score'])
            label = best_result['label']
            confidence = best_result['score']
            
            # Update stats
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            with self._lock:
                self.inference_stats['total_predictions'] += 1
                # Running average
                total = self.inference_stats['total_predictions']
                current_avg = self.inference_stats['avg_inference_time']
                self.inference_stats['avg_inference_time'] = (
                    (current_avg * (total - 1) + inference_time) / total
                )
            
            return label, confidence
            
        except Exception as e:
            logger.error(f"Prediction failed for text '{text[:50]}...': {e}")
            return "CLEAN", 0.0
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict if text is abusive.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with prediction results
        """
        if not text or not text.strip():
            return {
                'text': text,
                'is_abusive': False,
                'label': 'CLEAN',
                'confidence': 0.0,
                'inference_time_ms': 0.0
            }
        
        start_time = time.time()
        
        # Normalize text
        normalized_text = self.normalizer.normalize_text(text)
        
        # Check cache first
        try:
            label, confidence = self._cached_predict(normalized_text)
        except Exception as e:
            logger.error(f"Cached prediction failed: {e}")
            label, confidence = self._predict_single(text)
        
        # Determine if abusive based on threshold
        is_abusive = (label == "ABUSIVE" and confidence >= self.confidence_threshold)
        
        inference_time = (time.time() - start_time) * 1000
        
        return {
            'text': text,
            'normalized_text': normalized_text,
            'is_abusive': is_abusive,
            'label': label,
            'confidence': float(confidence),
            'inference_time_ms': float(inference_time),
            'threshold': self.confidence_threshold
        }
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict multiple texts efficiently.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of prediction results
        """
        if not texts:
            return []
        
        start_time = time.time()
        results = []
        
        # Process in batches for efficiency
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Normalize batch
            normalized_batch = [self.normalizer.normalize_text(text) for text in batch]
            
            try:
                # Batch prediction
                batch_results = self.pipeline(normalized_batch)
                
                # Process results
                for j, (original_text, normalized_text, pipeline_result) in enumerate(
                    zip(batch, normalized_batch, batch_results)
                ):
                    if isinstance(pipeline_result, list):
                        best_result = max(pipeline_result, key=lambda x: x['score'])
                    else:
                        best_result = pipeline_result
                    
                    label = best_result['label']
                    confidence = best_result['score']
                    is_abusive = (label == "ABUSIVE" and confidence >= self.confidence_threshold)
                    
                    results.append({
                        'text': original_text,
                        'normalized_text': normalized_text,
                        'is_abusive': is_abusive,
                        'label': label,
                        'confidence': float(confidence),
                        'threshold': self.confidence_threshold
                    })
                    
            except Exception as e:
                logger.error(f"Batch prediction failed: {e}")
                # Fallback to individual predictions
                for text in batch:
                    results.append(self.predict(text))
        
        total_time = (time.time() - start_time) * 1000
        
        # Update batch stats
        with self._lock:
            self.inference_stats['total_predictions'] += len(texts)
        
        logger.info(f"Batch prediction completed: {len(texts)} texts in {total_time:.2f}ms")
        
        return results
    
    def predict_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict abusive segments from Whisper transcript format.
        
        Args:
            segments: List of Whisper segments with 'text', 'start', 'end'
            
        Returns:
            List of abusive segments with predictions
        """
        if not segments:
            return []
        
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
                    'label': prediction['label'],
                    'confidence': prediction['confidence'],
                    'inference_time_ms': prediction['inference_time_ms'],
                    'normalized_text': prediction['normalized_text']
                }
                abusive_segments.append(abusive_segment)
        
        logger.info(f"Found {len(abusive_segments)} abusive segments out of {len(segments)} total segments")
        
        return abusive_segments
    
    def get_stats(self) -> Dict[str, Any]:
        """Get inference statistics."""
        with self._lock:
            stats = self.inference_stats.copy()
        
        cache_info = self._cached_predict.cache_info()
        stats.update({
            'cache_hits_ratio': cache_info.hits / max(cache_info.hits + cache_info.misses, 1),
            'cache_size': cache_info.currsize,
            'cache_maxsize': cache_info.maxsize,
            'device': self.device,
            'model_path': str(self.model_path)
        })
        
        return stats
    
    def clear_cache(self):
        """Clear the prediction cache."""
        self._cached_predict.cache_clear()
        logger.info("Prediction cache cleared")
    
    def update_threshold(self, new_threshold: float):
        """Update confidence threshold."""
        old_threshold = self.confidence_threshold
        self.confidence_threshold = new_threshold
        self.clear_cache()  # Clear cache as results may change
        logger.info(f"Confidence threshold updated: {old_threshold} -> {new_threshold}")

# Global inference instance for production use
_global_classifier: Optional[TransformerInference] = None

def get_transformer_classifier(
    model_path: Optional[str] = None,
    confidence_threshold: float = 0.7
) -> TransformerInference:
    """
    Get global transformer classifier instance.
    
    Args:
        model_path: Path to the model (required on first call)
        confidence_threshold: Confidence threshold
        
    Returns:
        TransformerInference instance
    """
    global _global_classifier
    
    if _global_classifier is None:
        if model_path is None:
            # Try default path
            default_path = Path("./models/abusive_classifier_indic/production")
            if default_path.exists():
                model_path = str(default_path)
            else:
                raise ValueError("model_path is required on first call")
        
        _global_classifier = TransformerInference(model_path, confidence_threshold)
    
    return _global_classifier

def predict_abusive(text: str) -> bool:
    """
    Simple function to check if text is abusive.
    
    Args:
        text: Input text
        
    Returns:
        True if abusive, False otherwise
    """
    classifier = get_transformer_classifier()
    result = classifier.predict(text)
    return result['is_abusive']

def predict_abusive_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Predict abusive segments from Whisper transcript.
    
    Args:
        segments: Whisper segments
        
    Returns:
        List of abusive segments
    """
    classifier = get_transformer_classifier()
    return classifier.predict_segments(segments)

def get_classifier_stats() -> Dict[str, Any]:
    """Get classifier statistics."""
    if _global_classifier is None:
        return {'status': 'not_initialized'}
    
    return _global_classifier.get_stats()
