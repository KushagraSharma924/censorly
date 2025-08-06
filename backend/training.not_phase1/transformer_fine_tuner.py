"""
Fine-tuning script for transformer models on abuse detection data.
Supports IndicBERT, MuRIL, and XLM-R for multilingual abuse detection.
"""

import os
import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
    DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import wandb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AbuseDataset(Dataset):
    """Dataset class for abuse detection training."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
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

class AbuseTrainer:
    """
    Fine-tuning trainer for multilingual abuse detection models.
    """
    
    def __init__(
        self,
        model_name: str = "ai4bharat/indic-bert",
        output_dir: str = "./models/fine_tuned_abuse_detector",
        max_length: int = 512,
        learning_rate: float = 2e-5,
        num_epochs: int = 3,
        batch_size: int = 16,
        use_wandb: bool = False
    ):
        """
        Initialize the trainer.
        
        Args:
            model_name: Hugging Face model name
            output_dir: Directory to save fine-tuned model
            max_length: Maximum sequence length
            learning_rate: Learning rate for training
            num_epochs: Number of training epochs
            batch_size: Training batch size
            use_wandb: Whether to use Weights & Biases for logging
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.max_length = max_length
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.use_wandb = use_wandb
        
        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model(self):
        """Load the pre-trained model and tokenizer."""
        logger.info(f"Loading model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=2,  # Binary classification
            trust_remote_code=True
        )
        
        self.model.to(self.device)
        logger.info("Model loaded successfully")
    
    def load_data(self, data_path: str) -> Tuple[List[str], List[int]]:
        """
        Load training data from JSON file.
        
        Expected format:
        [
            {"text": "sample text", "label": 0},
            {"text": "abusive text", "label": 1},
            ...
        ]
        
        Args:
            data_path: Path to training data JSON file
            
        Returns:
            Tuple of (texts, labels)
        """
        logger.info(f"Loading data from: {data_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = []
        labels = []
        
        for item in data:
            texts.append(item['text'])
            labels.append(int(item['label']))
        
        logger.info(f"Loaded {len(texts)} samples")
        logger.info(f"Label distribution: {np.bincount(labels)}")
        
        return texts, labels
    
    def prepare_datasets(self, texts: List[str], labels: List[int], test_size: float = 0.2):
        """Prepare training and validation datasets."""
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        logger.info(f"Training samples: {len(train_texts)}")
        logger.info(f"Validation samples: {len(val_texts)}")
        
        # Create datasets
        train_dataset = AbuseDataset(train_texts, train_labels, self.tokenizer, self.max_length)
        val_dataset = AbuseDataset(val_texts, val_labels, self.tokenizer, self.max_length)
        
        return train_dataset, val_dataset
    
    def compute_metrics(self, eval_pred):
        """Compute metrics for evaluation."""
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
    
    def train(self, train_dataset, val_dataset):
        """Train the model."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Initialize wandb if requested
        if self.use_wandb:
            wandb.init(
                project="abuse-detection",
                config={
                    "model_name": self.model_name,
                    "learning_rate": self.learning_rate,
                    "batch_size": self.batch_size,
                    "num_epochs": self.num_epochs,
                    "max_length": self.max_length
                }
            )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size * 2,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=str(self.output_dir / 'logs'),
            logging_steps=100,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=500,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            learning_rate=self.learning_rate,
            dataloader_pin_memory=True,
            report_to="wandb" if self.use_wandb else None,
            run_name=f"abuse-detection-{self.model_name.split('/')[-1]}" if self.use_wandb else None
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Create trainer
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
        
        # Train
        logger.info("Starting training...")
        self.trainer.train()
        
        # Save model
        self.trainer.save_model()
        self.tokenizer.save_pretrained(str(self.output_dir))
        
        logger.info(f"Model saved to: {self.output_dir}")
        
        if self.use_wandb:
            wandb.finish()
    
    def evaluate(self, val_dataset):
        """Evaluate the trained model."""
        if self.trainer is None:
            raise ValueError("Model not trained. Call train() first.")
        
        logger.info("Evaluating model...")
        eval_results = self.trainer.evaluate()
        
        logger.info("Evaluation Results:")
        for key, value in eval_results.items():
            logger.info(f"  {key}: {value:.4f}")
        
        return eval_results
    
    def predict(self, texts: List[str]) -> List[Dict]:
        """Make predictions on new texts."""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not loaded.")
        
        predictions = []
        
        for text in texts:
            # Tokenize
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=self.max_length,
                return_tensors='pt'
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                predicted_class = torch.argmax(logits, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            predictions.append({
                'text': text,
                'predicted_class': predicted_class,
                'is_abusive': predicted_class == 1,
                'confidence': confidence,
                'probabilities': probabilities[0].cpu().numpy().tolist()
            })
        
        return predictions

def main():
    """Main training script."""
    parser = argparse.ArgumentParser(description="Fine-tune transformer model for abuse detection")
    parser.add_argument("--model_name", default="ai4bharat/indic-bert", help="Hugging Face model name")
    parser.add_argument("--data_path", required=True, help="Path to training data JSON file")
    parser.add_argument("--output_dir", default="./models/fine_tuned_abuse_detector", help="Output directory")
    parser.add_argument("--max_length", type=int, default=512, help="Maximum sequence length")
    parser.add_argument("--learning_rate", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--num_epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--use_wandb", action="store_true", help="Use Weights & Biases logging")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test set size")
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = AbuseTrainer(
        model_name=args.model_name,
        output_dir=args.output_dir,
        max_length=args.max_length,
        learning_rate=args.learning_rate,
        num_epochs=args.num_epochs,
        batch_size=args.batch_size,
        use_wandb=args.use_wandb
    )
    
    # Load model
    trainer.load_model()
    
    # Load and prepare data
    texts, labels = trainer.load_data(args.data_path)
    train_dataset, val_dataset = trainer.prepare_datasets(texts, labels, args.test_size)
    
    # Train
    trainer.train(train_dataset, val_dataset)
    
    # Evaluate
    eval_results = trainer.evaluate(val_dataset)
    
    # Save evaluation results
    results_path = Path(args.output_dir) / "evaluation_results.json"
    with open(results_path, 'w') as f:
        json.dump(eval_results, f, indent=2)
    
    logger.info(f"Training completed. Results saved to {results_path}")

if __name__ == "__main__":
    main()
