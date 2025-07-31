#!/usr/bin/env python3
"""
🔥 BOOM TRAINER 🔥
Drop any CSV file and BOOM - it's trained!

Usage: python3 boom_train.py
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from universal_trainer import UniversalTrainer


def boom_train():
    """Auto-train with any CSV you've added."""
    
    
    print(" BOOM TRAINER - Auto CSV Training System")
   
    print(" Drop any CSV file in your project and BOOM - it's trained!")
    print(" Scanning for CSV files...")
    
    # Initialize the universal trainer
    trainer = UniversalTrainer()
    
    # Auto-discover and train with ALL CSV files
    results = trainer.train_all_datasets(auto_discover=True)
    
    # Generate report
    trainer.generate_report(results, "boom_training_report.txt")
    
    if results['success']:
        
        print(" BOOM! Training completed successfully!")
        print(f"Processed {results['total_words']} words from {results['datasets_processed']} datasets")
        print(" Your AI is now more powerful!")
        print(" Ready to detect profanity in multiple languages!")
        print(" Just add more CSV files and run this again to keep training!")
        print("" * 20)
    else:
        print("❌ Training failed. Check your CSV files and try again.")


if __name__ == "__main__":
    boom_train()
