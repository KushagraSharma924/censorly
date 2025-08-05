"""
Transformer-based abuse detection using IndicBERT, MuRIL, and XLM-R models.
Production-ready multilingual abuse detection for Hindi, Hinglish, and English.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import threading
import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline,
    logging as transformers_logging
)
import numpy as np

# Suppress transformers warnings
transformers_logging.set_verbosity_error()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransformerAbuseDetector:
    """
    Production transformer-based abuse detector supporting multiple multilingual models.
    
    Supported Models:
    - IndicBERT: ai4bharat/indic-bert for Indic languages
    - MuRIL: google/muril-base-cased for multilingual
    - XLM-R: xlm-roberta-base for cross-lingual
    - DistilBERT: distilbert-base-multilingual-cased (fallback)
    """
    
    def __init__(
        self,
        model_name: str = "ai4bharat/indic-bert",
        cache_dir: Optional[str] = None,
        device: Optional[str] = None,
        max_length: int = 512,
        batch_size: int = 16,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize transformer abuse detector.
        
        Args:
            model_name: Hugging Face model name
            cache_dir: Directory to cache models
            device: Device to run inference on ('cpu', 'cuda', 'mps')
            max_length: Maximum sequence length
            batch_size: Batch size for inference
            confidence_threshold: Confidence threshold for abuse detection
        """
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.confidence_threshold = confidence_threshold
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), '../models/transformers')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        self.device = device
        
        # Model states
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        self.model_info = {}
        self._lock = threading.Lock()
        
        logger.info(f"Initializing TransformerAbuseDetector with model: {model_name}")
        logger.info(f"Device: {device}, Cache: {cache_dir}")
        
    def load_model(self, force_reload: bool = False) -> bool:
        """
        Load the transformer model and tokenizer.
        
        Args:
            force_reload: Force reload even if already loaded
            
        Returns:
            bool: Success status
        """
        with self._lock:
            if self.is_loaded and not force_reload:
                return True
                
            try:
                logger.info(f"Loading transformer model: {self.model_name}")
                start_time = time.time()
                
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    cache_dir=str(self.cache_dir),
                    trust_remote_code=True
                )
                
                # Load model
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    cache_dir=str(self.cache_dir),
                    trust_remote_code=True,
                    num_labels=2  # Binary classification: abuse/not_abuse
                )
                
                # Move to device
                self.model.to(self.device)
                self.model.eval()
                
                # Create pipeline
                self.pipeline = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if self.device == 'cuda' else -1,
                    return_all_scores=True
                )
                
                load_time = time.time() - start_time
                self.is_loaded = True
                
                # Store model info
                self.model_info = {
                    'model_name': self.model_name,
                    'device': self.device,
                    'load_time_seconds': round(load_time, 2),
                    'max_length': self.max_length,
                    'confidence_threshold': self.confidence_threshold,
                    'model_size': self._estimate_model_size(),
                    'supported_languages': self._get_supported_languages()
                }
                
                logger.info(f"Model loaded successfully in {load_time:.2f}s")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                self.is_loaded = False
                return False
    
    def _estimate_model_size(self) -> str:
        """Estimate model size in memory."""
        if self.model is None:
            return "Unknown"
        
        try:
            param_count = sum(p.numel() for p in self.model.parameters())
            size_mb = (param_count * 4) / (1024 * 1024)  # Assuming float32
            
            if size_mb < 1024:
                return f"{size_mb:.1f}MB"
            else:
                return f"{size_mb/1024:.1f}GB"
        except:
            return "Unknown"
    
    def _get_supported_languages(self) -> List[str]:
        """Get supported languages based on model."""
        model_lang_map = {
            'indic-bert': ['hi', 'en', 'bn', 'gu', 'mr', 'ta', 'te', 'kn', 'ml', 'or', 'pa', 'as'],
            'muril': ['hi', 'en', 'bn', 'gu', 'mr', 'ta', 'te', 'kn', 'ml', 'or', 'pa', 'as', 'ur'],
            'xlm-roberta': ['en', 'hi', 'ar', 'bg', 'de', 'el', 'es', 'fr', 'ru', 'th', 'tr', 'vi', 'zh'],
            'distilbert': ['en', 'hi', 'ar', 'de', 'es', 'fr', 'it', 'pt', 'ru', 'zh']
        }
        
        for key, langs in model_lang_map.items():
            if key in self.model_name.lower():
                return langs
        
        return ['en', 'hi']  # Default fallback
    
    def predict(
        self, 
        text: str, 
        return_score: bool = True,
        return_probabilities: bool = False
    ) -> Dict[str, Any]:
        """
        Predict abuse for a single text.
        
        Args:
            text: Input text to analyze
            return_score: Include confidence score
            return_probabilities: Include class probabilities
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load transformer model")
        
        if not text or not text.strip():
            return {
                'is_abusive': False,
                'confidence': 0.0,
                'text': text,
                'method': 'transformer',
                'model_name': self.model_name
            }
        
        try:
            start_time = time.time()
            
            # Truncate text if too long
            if len(text) > self.max_length * 2:  # Rough character limit
                text = text[:self.max_length * 2]
            
            # Get prediction
            results = self.pipeline(text)
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Parse results - assuming labels are 'ABUSE' and 'NOT_ABUSE' or similar
            abuse_score = 0.0
            for result in results[0]:
                label = result['label'].upper()
                if 'ABUSE' in label or 'TOXIC' in label or 'OFFENSIVE' in label or label == 'LABEL_1':
                    abuse_score = result['score']
                    break
                elif 'NOT' in label or 'CLEAN' in label or label == 'LABEL_0':
                    abuse_score = 1.0 - result['score']  # Invert for abuse score
            
            is_abusive = abuse_score >= self.confidence_threshold
            
            result = {
                'is_abusive': is_abusive,
                'confidence': round(abuse_score, 4),
                'text': text,
                'method': 'transformer',
                'model_name': self.model_name,
                'inference_time_ms': round(inference_time, 2)
            }
            
            if return_probabilities:
                result['probabilities'] = {
                    res['label']: round(res['score'], 4) 
                    for res in results[0]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Transformer prediction error: {e}")
            return {
                'is_abusive': False,
                'confidence': 0.0,
                'text': text,
                'method': 'transformer',
                'model_name': self.model_name,
                'error': str(e)
            }
    
    def predict_batch(
        self, 
        texts: List[str], 
        return_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Predict abuse for multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            return_scores: Include confidence scores
            
        Returns:
            List of prediction results
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load transformer model")
        
        if not texts:
            return []
        
        try:
            start_time = time.time()
            
            # Filter and prepare texts
            valid_texts = []
            text_indices = []
            
            for i, text in enumerate(texts):
                if text and text.strip():
                    # Truncate if too long
                    if len(text) > self.max_length * 2:
                        text = text[:self.max_length * 2]
                    valid_texts.append(text)
                    text_indices.append(i)
            
            if not valid_texts:
                return [
                    {
                        'is_abusive': False,
                        'confidence': 0.0,
                        'text': text,
                        'method': 'transformer',
                        'model_name': self.model_name
                    }
                    for text in texts
                ]
            
            # Batch prediction
            results = self.pipeline(valid_texts, batch_size=self.batch_size)
            inference_time = (time.time() - start_time) * 1000
            
            # Parse results
            predictions = []
            valid_idx = 0
            
            for i, original_text in enumerate(texts):
                if i in text_indices:
                    # Process valid text result
                    text_results = results[valid_idx]
                    
                    abuse_score = 0.0
                    for result in text_results:
                        label = result['label'].upper()
                        if 'ABUSE' in label or 'TOXIC' in label or 'OFFENSIVE' in label or label == 'LABEL_1':
                            abuse_score = result['score']
                            break
                        elif 'NOT' in label or 'CLEAN' in label or label == 'LABEL_0':
                            abuse_score = 1.0 - result['score']
                    
                    is_abusive = abuse_score >= self.confidence_threshold
                    
                    prediction = {
                        'is_abusive': is_abusive,
                        'confidence': round(abuse_score, 4),
                        'text': original_text,
                        'method': 'transformer',
                        'model_name': self.model_name
                    }
                    
                    if return_scores:
                        prediction['inference_time_ms'] = round(inference_time / len(valid_texts), 2)
                    
                    predictions.append(prediction)
                    valid_idx += 1
                else:
                    # Empty or invalid text
                    predictions.append({
                        'is_abusive': False,
                        'confidence': 0.0,
                        'text': original_text,
                        'method': 'transformer',
                        'model_name': self.model_name
                    })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return [
                {
                    'is_abusive': False,
                    'confidence': 0.0,
                    'text': text,
                    'method': 'transformer',
                    'model_name': self.model_name,
                    'error': str(e)
                }
                for text in texts
            ]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and statistics."""
        return {
            **self.model_info,
            'is_loaded': self.is_loaded,
            'device_available': {
                'cuda': torch.cuda.is_available(),
                'mps': hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(),
                'cpu': True
            }
        }
    
    def unload_model(self):
        """Unload model to free memory."""
        with self._lock:
            if self.model is not None:
                del self.model
                self.model = None
            
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            
            if self.pipeline is not None:
                del self.pipeline
                self.pipeline = None
            
            self.is_loaded = False
            
            # Clear GPU cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded successfully")


class MultiModelTransformerDetector:
    """
    Ensemble detector using multiple transformer models for robust detection.
    """
    
    def __init__(self, models_config: Optional[Dict[str, Dict]] = None):
        """
        Initialize multi-model detector.
        
        Args:
            models_config: Configuration for each model
        """
        if models_config is None:
            models_config = {
                'indic_bert': {
                    'model_name': 'ai4bharat/indic-bert',
                    'weight': 0.4,
                    'languages': ['hi', 'en']
                },
                'muril': {
                    'model_name': 'google/muril-base-cased',
                    'weight': 0.4,
                    'languages': ['hi', 'en']
                },
                'xlm_roberta': {
                    'model_name': 'xlm-roberta-base',
                    'weight': 0.2,
                    'languages': ['en', 'hi']
                }
            }
        
        self.models_config = models_config
        self.models = {}
        self.is_initialized = False
        
    def initialize(self, load_on_demand: bool = True) -> bool:
        """Initialize all models."""
        try:
            for name, config in self.models_config.items():
                model = TransformerAbuseDetector(
                    model_name=config['model_name'],
                    confidence_threshold=0.7
                )
                
                if not load_on_demand:
                    if not model.load_model():
                        logger.warning(f"Failed to load model {name}")
                        continue
                
                self.models[name] = {
                    'detector': model,
                    'config': config
                }
                
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize multi-model detector: {e}")
            return False
    
    def predict(self, text: str, language_hint: str = 'auto') -> Dict[str, Any]:
        """
        Predict using ensemble of models.
        
        Args:
            text: Input text
            language_hint: Language hint for model selection
            
        Returns:
            Ensemble prediction result
        """
        if not self.is_initialized:
            self.initialize()
        
        predictions = {}
        weighted_score = 0.0
        total_weight = 0.0
        
        for name, model_info in self.models.items():
            try:
                detector = model_info['detector']
                config = model_info['config']
                
                # Skip if language not supported
                if language_hint != 'auto' and language_hint not in config['languages']:
                    continue
                
                result = detector.predict(text, return_score=True)
                predictions[name] = result
                
                if 'error' not in result:
                    weight = config['weight']
                    weighted_score += result['confidence'] * weight
                    total_weight += weight
                
            except Exception as e:
                logger.error(f"Error in model {name}: {e}")
                continue
        
        if total_weight > 0:
            final_confidence = weighted_score / total_weight
            is_abusive = final_confidence >= 0.7
        else:
            final_confidence = 0.0
            is_abusive = False
        
        return {
            'is_abusive': is_abusive,
            'confidence': round(final_confidence, 4),
            'text': text,
            'method': 'ensemble_transformer',
            'model_predictions': predictions,
            'ensemble_weights': {
                name: info['config']['weight'] 
                for name, info in self.models.items()
            }
        }


# Factory function for easy instantiation
def create_transformer_detector(
    model_type: str = 'indic_bert',
    **kwargs
) -> TransformerAbuseDetector:
    """
    Factory function to create transformer detector.
    
    Args:
        model_type: Type of model ('indic_bert', 'muril', 'xlm_roberta', 'distilbert')
        **kwargs: Additional arguments
        
    Returns:
        TransformerAbuseDetector instance
    """
    model_map = {
        'indic_bert': 'ai4bharat/indic-bert',
        'muril': 'google/muril-base-cased',
        'xlm_roberta': 'xlm-roberta-base',
        'distilbert': 'distilbert-base-multilingual-cased'
    }
    
    model_name = model_map.get(model_type, model_map['indic_bert'])
    return TransformerAbuseDetector(model_name=model_name, **kwargs)


# Global instance for reuse
_global_detector = None

def get_global_detector(model_type: str = 'indic_bert') -> TransformerAbuseDetector:
    """Get or create global transformer detector instance."""
    global _global_detector
    
    if _global_detector is None:
        _global_detector = create_transformer_detector(model_type)
    
    return _global_detector
