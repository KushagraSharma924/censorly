"""
Production-ready abuse classification service.
Supports HuggingFace transformers and scikit-learn models with graceful fallback.
"""

import os
import pickle
import logging
from typing import Optional, Dict, Any, Union, List

logger = logging.getLogger(__name__)

# Optional imports with fallback
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Global classifier instance
_global_classifier = None


class AbuseClassifier:
    """
    Unified abuse classifier supporting multiple model types.
    """
    
    def __init__(self, model_path: Optional[str] = None, model_type: str = "auto"):
        """
        Initialize the abuse classifier.
        
        Args:
            model_path: Path to the model file or HuggingFace model name
            model_type: Type of model ("huggingface", "sklearn", or "auto")
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.vectorizer = None
        self.metadata = {}
        self.is_loaded = False
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load the appropriate model based on type."""
        if model_path:
            self.model_path = model_path
            
        if not self.model_path:
            logger.warning("No model path provided")
            return False
            
        try:
            if self.model_type == "auto":
                self.model_type = self._detect_model_type()
            
            if self.model_type == "huggingface":
                self._load_huggingface_model()
            elif self.model_type == "sklearn":
                self._load_sklearn_model()
            else:
                logger.error(f"Unsupported model type: {self.model_type}")
                return False
                
            self.is_loaded = True
            logger.info(f"Successfully loaded {self.model_type} model from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_loaded = False
            return False
    
    def _detect_model_type(self) -> str:
        """Auto-detect model type based on file/path."""
        if not self.model_path:
            return "sklearn"
            
        if isinstance(self.model_path, str):
            if self.model_path.endswith(('.pkl', '.pickle', '.joblib')):
                return "sklearn"
            elif os.path.isdir(self.model_path) or '/' in self.model_path:
                return "huggingface"
        
        # Default to sklearn for compatibility
        return "sklearn"
    
    def _load_huggingface_model(self) -> None:
        """Load HuggingFace transformer model."""
        if not HAS_TRANSFORMERS:
            raise Exception("transformers library not available")
            
        if not self.model_path:
            raise Exception("No model path provided for HuggingFace model")
        
        try:
            if os.path.isdir(self.model_path):
                # Local model directory
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = pipeline(
                    "text-classification",
                    model=self.model_path,
                    tokenizer=self.tokenizer,
                    return_all_scores=True
                )
            else:
                # HuggingFace Hub model
                self.model = pipeline(
                    "text-classification",
                    model=self.model_path,
                    return_all_scores=True
                )
        except Exception as e:
            raise Exception(f"Failed to load HuggingFace model: {e}")
    
    def _load_sklearn_model(self) -> None:
        """Load scikit-learn model."""
        if not self.model_path:
            raise Exception("No model path provided for sklearn model")
            
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            if isinstance(model_data, dict):
                # Model saved with metadata
                self.model = model_data['model']
                self.vectorizer = model_data.get('vectorizer')
                self.metadata = model_data.get('metadata', {})
            else:
                # Just the model
                self.model = model_data
                
        except Exception as e:
            raise Exception(f"Failed to load sklearn model: {e}")
    
    def predict(self, text: str, return_score: bool = False) -> Union[bool, Dict[str, Any]]:
        """
        Predict if text is abusive.
        
        Args:
            text: Text to classify
            return_score: Whether to return confidence scores
            
        Returns:
            Boolean prediction or dict with scores if return_score=True
        """
        if not self.is_loaded or not self.model:
            if return_score:
                return {
                    'is_abusive': False,
                    'confidence': 0.0,
                    'error': 'Model not loaded',
                    'model_type': self.model_type
                }
            return False
        
        try:
            if self.model_type == "huggingface":
                return self._predict_huggingface(text, return_score)
            elif self.model_type == "sklearn":
                return self._predict_sklearn(text, return_score)
            else:
                if return_score:
                    return {
                        'is_abusive': False,
                        'confidence': 0.0,
                        'error': f'Unsupported model type: {self.model_type}',
                        'model_type': self.model_type
                    }
                return False
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            if return_score:
                return {
                    'is_abusive': False,
                    'confidence': 0.0,
                    'error': str(e),
                    'model_type': self.model_type
                }
            return False
    
    def _predict_huggingface(self, text: str, return_score: bool = False) -> Union[bool, Dict[str, Any]]:
        """Predict using HuggingFace model."""
        if not self.model:
            raise Exception("HuggingFace model not loaded")
        
        try:
            result = self.model(text)
            
            # Find abuse/toxic label
            toxic_score = 0.0
            for item in result[0]:
                label = item['label'].lower()
                if 'toxic' in label or 'abuse' in label or 'negative' in label or label == 'LABEL_1':
                    toxic_score = item['score']
                    break
            
            is_abusive = toxic_score > 0.5
            
            if not return_score:
                return is_abusive
            
            return {
                'is_abusive': is_abusive,
                'confidence': float(toxic_score),
                'model_type': 'huggingface',
                'raw_output': result[0]
            }
            
        except Exception as e:
            raise Exception(f"HuggingFace prediction failed: {e}")
    
    def _predict_sklearn(self, text: str, return_score: bool = False) -> Union[bool, Dict[str, Any]]:
        """Predict using scikit-learn model."""
        if not self.model:
            if return_score:
                return {
                    'is_abusive': False,
                    'confidence': 0.0,
                    'error': 'Model not loaded',
                    'model_type': self.model_type
                }
            return False
            
        # Get prediction directly from model (pipeline handles vectorization)
        try:
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba([text])[0]
                abuse_probability = float(probabilities[1]) if len(probabilities) > 1 else 0.0
                is_abusive = abuse_probability > 0.5
                confidence = abuse_probability  # Always return probability of being abusive
            else:
                prediction = self.model.predict([text])[0]
                is_abusive = bool(prediction)
                confidence = 1.0 if is_abusive else 0.0
            
            if not return_score:
                return is_abusive
            
            return {
                'is_abusive': is_abusive,
                'confidence': confidence,
                'model_type': 'sklearn'
            }
            
        except Exception as e:
            raise Exception(f"Sklearn prediction failed: {e}")
    
    def predict_batch(self, texts: List[str], return_scores: bool = False) -> List[Union[bool, Dict[str, Any]]]:
        """
        Predict multiple texts in batch.
        
        Args:
            texts: List of texts to classify
            return_scores: Whether to return confidence scores
            
        Returns:
            List of predictions
        """
        results = []
        for text in texts:
            try:
                result = self.predict(text, return_score=return_scores)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch prediction error for text '{text[:50]}...': {e}")
                if return_scores:
                    results.append({
                        'is_abusive': False,
                        'confidence': 0.0,
                        'error': str(e),
                        'model_type': self.model_type
                    })
                else:
                    results.append(False)
        
        return results


def load_classifier(model_path: Optional[str] = None) -> AbuseClassifier:
    """
    Load and return a global abuse classifier instance.
    
    Args:
        model_path: Optional path to model file. If None, uses default paths.
        
    Returns:
        AbuseClassifier instance
    """
    global _global_classifier
    
    if _global_classifier is None:
        _global_classifier = AbuseClassifier()
        
        # Try multiple model paths for production
        model_paths = [
            model_path,
            './models/test_abuse_classifier.pkl',  # Production model
            './models/abuse_classifier.pkl',
            './models/abuse_classifier_v2.pkl', 
            './models/transformer_model',
            './models/huggingface_model',
            os.path.join(os.path.dirname(__file__), '../models/test_abuse_classifier.pkl'),
            os.path.join(os.path.dirname(__file__), '../models/abuse_classifier.pkl')
        ]
        
        model_loaded = False
        for path in model_paths:
            if path and os.path.exists(path) and _global_classifier.load_model(path):
                model_loaded = True
                logger.info(f"Successfully loaded model from: {path}")
                break
        
        if not model_loaded:
            logger.warning("No abuse classification model found. System will use fallback detection.")
    
    return _global_classifier


def get_classifier_info() -> Dict[str, Any]:
    """
    Get information about the currently loaded classifier.
    
    Returns:
        Dictionary with classifier information
    """
    try:
        classifier = load_classifier()
        
        if classifier.is_loaded:
            return {
                'model_path': classifier.model_path,
                'model_type': classifier.model_type,
                'is_loaded': True,
                'has_vectorizer': classifier.vectorizer is not None,
                'supports_batch': True
            }
        else:
            return {
                'error': 'No model loaded',
                'is_loaded': False,
                'available_paths': [
                    './models/abuse_classifier.pkl',
                    './models/transformer_model'
                ]
            }
    except Exception as e:
        return {
            'error': str(e),
            'is_loaded': False
        }


def reset_classifier():
    """Reset the global classifier instance."""
    global _global_classifier
    _global_classifier = None
