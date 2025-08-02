"""
Fine-tuning transformer models for multilingual abusive language detection.
Supports Hindi, Hinglish, and English with production-ready optimization.
"""

import os
import json
import pandas as pd
import numpy as np
import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Any
import logging
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, pipeline,
    EarlyStoppingCallback, DataCollatorWithPadding
)

import wandb
from tqdm import tqdm

logger = logging.getLogger(__name__)

class TextNormalizer:
    """Enhanced text normalization for abusive language detection."""
    
    def __init__(self):
        # Character substitution mapping for obfuscation handling
        self.char_map = str.maketrans({
            '@': 'a', '$': 's', '3': 'e', '1': 'i', '0': 'o',
            '4': 'a', '5': 's', '7': 't', '8': 'b', '!': 'i',
            '€': 'e', '£': 'l', '6': 'g', '9': 'g', '+': 't',
            '*': '', '#': '', '%': '', '&': 'and'
        })
        
        # Leet speak patterns
        self.leet_patterns = [
            (r'ph', 'f'), (r'x+', 'x'), (r'z+', 's'),
            (r'ck', 'k'), (r'qu', 'k'), (r'c', 'k'),
            (r'(\w)\1{2,}', r'\1\1')  # Reduce repeated chars
        ]
        
        # Hindi romanization normalization
        self.hindi_patterns = [
            (r'bh([aeiou])', r'b\1'), (r'ch([aeiou])', r'c\1'),
            (r'dh([aeiou])', r'd\1'), (r'gh([aeiou])', r'g\1'),
            (r'jh([aeiou])', r'j\1'), (r'kh([aeiou])', r'k\1'),
            (r'ph([aeiou])', r'f\1'), (r'th([aeiou])', r't\1'),
            (r'aa', 'a'), (r'ee', 'i'), (r'oo', 'u'),
            (r'([aeiou])\1+', r'\1')  # Reduce vowel repetition
        ]
    
    def normalize_text(self, text: str) -> str:
        """
        Comprehensive text normalization.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase and strip
        text = text.lower().strip()
        
        # Handle Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Apply character substitutions
        text = text.translate(self.char_map)
        
        # Apply leet speak normalization
        for pattern, replacement in self.leet_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Apply Hindi romanization normalization
        for pattern, replacement in self.hindi_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Clean excessive punctuation and whitespace
        text = re.sub(r'[^\w\s\u0900-\u097F\u0600-\u06FF]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

class AbusiveLanguageDataset(Dataset):
    """PyTorch Dataset for abusive language classification."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.normalizer = TextNormalizer()
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        
        # Normalize text
        text = self.normalizer.normalize_text(text)
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class TransformerTrainer:
    """
    Fine-tuning trainer for multilingual abusive language detection.
    Optimized for production deployment with fast inference.
    """
    
    def __init__(
        self,
        model_name: str = "ai4bharat/indic-bert",
        max_length: int = 128,
        output_dir: str = "./models/abusive_classifier",
        use_wandb: bool = False
    ):
        """
        Initialize the trainer.
        
        Args:
            model_name: Pre-trained model name (IndicBERT, MuRIL, etc.)
            max_length: Maximum sequence length
            output_dir: Directory to save the model
            use_wandb: Whether to use Weights & Biases for logging
        """
        self.model_name = model_name
        self.max_length = max_length
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_wandb = use_wandb
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.trainer = None
        self.normalizer = TextNormalizer()
        
        # Performance tracking
        self.training_stats = {}
        
        logger.info(f"Initialized TransformerTrainer with model: {model_name}")
    
    def load_data(self, data_path: str) -> Tuple[List[str], List[int]]:
        """
        Load training data from JSON or CSV file.
        
        Args:
            data_path: Path to the dataset file
            
        Returns:
            Tuple of (texts, labels)
        """
        data_path = Path(data_path)
        
        if data_path.suffix.lower() == '.json':
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                texts = [item['text'] for item in data]
                labels = [item['label'] for item in data]
            else:
                raise ValueError("JSON should contain a list of {'text': ..., 'label': ...} objects")
                
        elif data_path.suffix.lower() == '.csv':
            df = pd.read_csv(data_path)
            texts = df['text'].tolist()
            labels = df['label'].tolist()
        else:
            raise ValueError("Supported formats: .json, .csv")
        
        logger.info(f"Loaded {len(texts)} samples from {data_path}")
        
        # Validate labels
        unique_labels = set(labels)
        if not unique_labels.issubset({0, 1}):
            raise ValueError("Labels must be 0 (clean) or 1 (abusive)")
        
        label_counts = pd.Series(labels).value_counts()
        logger.info(f"Label distribution: {dict(label_counts)}")
        
        return texts, labels
    
    def create_sample_dataset(self, output_path: str = "sample_dataset.json"):
        """Create a sample dataset for testing."""
        sample_data = [
            # Clean samples
            {"text": "Hello how are you today", "label": 0},
            {"text": "Good morning everyone", "label": 0},
            {"text": "Aap kaise hain", "label": 0},
            {"text": "Nice weather today", "label": 0},
            {"text": "Thank you very much", "label": 0},
            {"text": "Namaste ji", "label": 0},
            {"text": "Have a great day", "label": 0},
            {"text": "Kya haal hai", "label": 0},
            
            # Abusive samples - Hindi
            {"text": "Tu chutiya hai", "label": 1},
            {"text": "Madarchod saala", "label": 1},
            {"text": "Bhenchod kya kar raha hai", "label": 1},
            {"text": "Randi ke bacche", "label": 1},
            {"text": "Gandu insaan", "label": 1},
            {"text": "Harami aadmi", "label": 1},
            {"text": "Kamina saala", "label": 1},
            {"text": "Bhen ki chut", "label": 1},
            
            # Abusive samples - English
            {"text": "You are a fucking idiot", "label": 1},
            {"text": "Shut the hell up", "label": 1},
            {"text": "Go to hell bastard", "label": 1},
            {"text": "You piece of shit", "label": 1},
            {"text": "Damn this fucking thing", "label": 1},
            {"text": "What a bitch", "label": 1},
            
            # Obfuscated samples
            {"text": "Tu chut1ya hai", "label": 1},
            {"text": "F*ck this sh1t", "label": 1},
            {"text": "B@stard madarch0d", "label": 1},
            {"text": "Go 2 h3ll", "label": 1},
            {"text": "What th3 f**k", "label": 1},
            
            # Hinglish samples
            {"text": "BC yaar tu pagal hai", "label": 1},
            {"text": "MC sab kharab hai", "label": 1},
            {"text": "WTF is this yaar", "label": 1},
            {"text": "Bkl tu samjha nahi", "label": 1}
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created sample dataset with {len(sample_data)} samples at {output_path}")
        return output_path
    
    def prepare_model(self):
        """Load and prepare the pre-trained model and tokenizer."""
        logger.info(f"Loading model and tokenizer: {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=2,
            id2label={0: "CLEAN", 1: "ABUSIVE"},
            label2id={"CLEAN": 0, "ABUSIVE": 1}
        )
        
        # Add special tokens if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
        
        logger.info("Model and tokenizer loaded successfully")
    
    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics."""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'f1': f1,
            'precision': precision,
            'recall': recall
        }
    
    def train(
        self,
        train_texts: List[str],
        train_labels: List[int],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[int]] = None,
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        warmup_steps: int = 100,
        weight_decay: float = 0.01,
        eval_steps: int = 50,
        save_steps: int = 100
    ):
        """
        Train the model.
        
        Args:
            train_texts: Training texts
            train_labels: Training labels
            val_texts: Validation texts (optional)
            val_labels: Validation labels (optional)
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            warmup_steps: Warmup steps
            weight_decay: Weight decay
            eval_steps: Evaluation frequency
            save_steps: Save frequency
        """
        if self.model is None or self.tokenizer is None:
            self.prepare_model()
        
        # Split data if validation not provided
        if val_texts is None or val_labels is None:
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                train_texts, train_labels, test_size=0.2, random_state=42, stratify=train_labels
            )
        
        logger.info(f"Training samples: {len(train_texts)}, Validation samples: {len(val_texts)}")
        
        # Create datasets
        train_dataset = AbusiveLanguageDataset(train_texts, train_labels, self.tokenizer, self.max_length)
        val_dataset = AbusiveLanguageDataset(val_texts, val_labels, self.tokenizer, self.max_length)
        
        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=warmup_steps,
            weight_decay=weight_decay,
            learning_rate=learning_rate,
            logging_dir=str(self.output_dir / 'logs'),
            logging_steps=10,
            eval_steps=eval_steps,
            save_steps=save_steps,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            save_total_limit=2,
            report_to="wandb" if self.use_wandb else None,
            run_name=f"abusive-classifier-{self.model_name.split('/')[-1]}" if self.use_wandb else None
        )
        
        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Start training
        logger.info("Starting training...")
        self.trainer.train()
        
        # Save final model
        self.trainer.save_model(str(self.output_dir / 'final'))
        self.tokenizer.save_pretrained(str(self.output_dir / 'final'))
        
        # Evaluate
        eval_results = self.trainer.evaluate()
        self.training_stats = eval_results
        
        logger.info(f"Training completed. Final metrics: {eval_results}")
        
        return eval_results
    
    def create_pipeline(self, model_path: Optional[str] = None) -> Any:
        """
        Create a HuggingFace pipeline for inference.
        
        Args:
            model_path: Path to the trained model (optional)
            
        Returns:
            HuggingFace pipeline object
        """
        if model_path is None:
            model_path = str(self.output_dir / 'final')
        
        # Load the fine-tuned model
        classifier = pipeline(
            "text-classification",
            model=model_path,
            tokenizer=model_path,
            device=0 if torch.cuda.is_available() else -1,
            return_all_scores=True
        )
        
        logger.info(f"Created pipeline from model: {model_path}")
        return classifier
    
    def optimize_for_production(self, model_path: Optional[str] = None):
        """
        Optimize the model for production deployment.
        
        Args:
            model_path: Path to the model to optimize
        """
        if model_path is None:
            model_path = str(self.output_dir / 'final')
        
        # Load model
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Convert to eval mode
        model.eval()
        
        # Optimize for inference
        if torch.cuda.is_available():
            model = model.half()  # Use half precision for faster inference
        
        # Save optimized model
        optimized_path = self.output_dir / 'production'
        optimized_path.mkdir(exist_ok=True)
        
        model.save_pretrained(str(optimized_path))
        tokenizer.save_pretrained(str(optimized_path))
        
        # Create production config
        config = {
            'model_name': self.model_name,
            'max_length': self.max_length,
            'training_stats': self.training_stats,
            'optimization': {
                'half_precision': torch.cuda.is_available(),
                'max_inference_time_ms': 100
            }
        }
        
        with open(optimized_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Optimized model saved to: {optimized_path}")
        return str(optimized_path)
    
    def benchmark_inference(self, model_path: Optional[str] = None, num_samples: int = 100):
        """
        Benchmark inference speed.
        
        Args:
            model_path: Path to the model
            num_samples: Number of samples to test
            
        Returns:
            Benchmark results
        """
        import time
        
        if model_path is None:
            model_path = str(self.output_dir / 'final')
        
        # Create pipeline
        classifier = self.create_pipeline(model_path)
        
        # Test samples
        test_texts = [
            "Hello how are you",
            "Tu chutiya hai",
            "What the fuck",
            "Namaste ji",
            "BC yaar",
            "Good morning"
        ] * (num_samples // 6 + 1)
        test_texts = test_texts[:num_samples]
        
        # Warm up
        for _ in range(5):
            classifier(test_texts[0])
        
        # Benchmark
        start_time = time.time()
        for text in test_texts:
            classifier(text)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_ms = (total_time / num_samples) * 1000
        
        benchmark_results = {
            'total_samples': num_samples,
            'total_time_s': total_time,
            'avg_time_ms': avg_time_ms,
            'samples_per_second': num_samples / total_time,
            'meets_requirement': avg_time_ms < 100
        }
        
        logger.info(f"Benchmark results: {benchmark_results}")
        return benchmark_results

def main():
    """Example usage of the TransformerTrainer."""
    # Initialize trainer with IndicBERT (good for Hindi/English)
    trainer = TransformerTrainer(
        model_name="ai4bharat/indic-bert",
        max_length=128,
        output_dir="./models/abusive_classifier_indic",
        use_wandb=False
    )
    
    # Create sample dataset
    dataset_path = trainer.create_sample_dataset("sample_abusive_dataset.json")
    
    # Load data
    texts, labels = trainer.load_data(dataset_path)
    
    # Train model
    results = trainer.train(
        train_texts=texts,
        train_labels=labels,
        num_epochs=3,
        batch_size=8,  # Small batch for demo
        learning_rate=2e-5
    )
    
    # Optimize for production
    production_path = trainer.optimize_for_production()
    
    # Benchmark
    benchmark = trainer.benchmark_inference(production_path)
    
    print(f"Training completed!")
    print(f"Final F1 Score: {results['eval_f1']:.4f}")
    print(f"Average inference time: {benchmark['avg_time_ms']:.2f}ms")
    print(f"Meets requirement (<100ms): {benchmark['meets_requirement']}")

if __name__ == "__main__":
    main()
