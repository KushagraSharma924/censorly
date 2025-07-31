#!/usr/bin/env python3
"""
Universal Profanity Training System
Automatically detects and trains with any CSV profanity dataset you add.
Supports multiple formats and languages.
"""

import csv
import json
import os
import sys
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import argparse

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from services.profanity_detection import (
    add_custom_profanity_words, 
    add_language_support,
    test_profanity_detection,
    ALL_ABUSIVE_WORDS,
    PROFANITY_PATTERNS
)


class UniversalTrainer:
    """Universal profanity detection trainer that can handle any CSV format."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the universal trainer.
        
        Args:
            data_dir: Directory to scan for CSV files (defaults to workspace root)
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent
        self.learned_words_path = Path("data/wordlists/learned_words.json")
        self.supported_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        self.trained_datasets = []
        
    def detect_csv_format(self, csv_path: Path) -> Dict[str, Any]:
        """
        Automatically detect CSV format and structure.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Format information dictionary
        """
        format_info = {
            'columns': [],
            'has_header': False,
            'delimiter': ',',
            'encoding': 'utf-8',
            'sample_rows': [],
            'detected_format': 'unknown'
        }
        
        # Try different encodings
        for encoding in self.supported_encodings:
            try:
                with open(csv_path, 'r', encoding=encoding) as file:
                    # Try different delimiters
                    for delimiter in [',', ';', '\t', '|']:
                        file.seek(0)
                        csv_reader = csv.reader(file, delimiter=delimiter)
                        rows = []
                        
                        for i, row in enumerate(csv_reader):
                            if i >= 5:  # Read first 5 rows for analysis
                                break
                            rows.append(row)
                        
                        if rows and len(rows[0]) >= 2:  # Must have at least 2 columns
                            format_info.update({
                                'encoding': encoding,
                                'delimiter': delimiter,
                                'sample_rows': rows,
                                'columns': len(rows[0]) if rows else 0
                            })
                            
                            # Detect format type
                            format_info['detected_format'] = self._detect_format_type(rows)
                            
                            print(f"✅ Detected format for {csv_path.name}: {format_info['detected_format']}")
                            print(f"   Encoding: {encoding}, Delimiter: '{delimiter}', Columns: {format_info['columns']}")
                            return format_info
                            
            except (UnicodeDecodeError, Exception):
                continue
        
        print(f"❌ Could not detect format for {csv_path.name}")
        return format_info
    
    def _detect_format_type(self, rows: List[List[str]]) -> str:
        """Detect the type of CSV format based on content analysis."""
        if not rows:
            return 'unknown'
        
        first_row = rows[0]
        
        # Check for common header patterns
        headers = [col.lower().strip() for col in first_row]
        
        if any(keyword in ' '.join(headers) for keyword in ['word', 'term', 'profanity', 'severity', 'meaning']):
            return 'standard_profanity'
        
        # Check column count and content patterns
        if len(first_row) == 3:
            # Might be word, meaning, severity format
            if rows[1:] and self._is_numeric(rows[1][2]):
                return 'word_meaning_severity'
        
        if len(first_row) == 2:
            # Might be word, category or word, meaning format
            return 'word_category'
        
        if len(first_row) == 1:
            # Simple word list
            return 'simple_wordlist'
        
        return 'custom_format'
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric."""
        try:
            float(value.strip())
            return True
        except (ValueError, AttributeError):
            return False
    
    def load_csv_dataset(self, csv_path: Path, language_hint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load any CSV dataset and convert to standard format.
        
        Args:
            csv_path: Path to CSV file
            language_hint: Optional language hint for categorization
            
        Returns:
            List of standardized word dictionaries
        """
        print(f"\n📂 Loading dataset: {csv_path.name}")
        
        # Detect format
        format_info = self.detect_csv_format(csv_path)
        if format_info['detected_format'] == 'unknown':
            print(f"⚠️ Could not process {csv_path.name} - unknown format")
            return []
        
        words_data = []
        
        try:
            with open(csv_path, 'r', encoding=format_info['encoding']) as file:
                csv_reader = csv.reader(file, delimiter=format_info['delimiter'])
                
                # Skip header if detected
                if format_info['detected_format'] in ['standard_profanity']:
                    next(csv_reader, None)
                
                for row_num, row in enumerate(csv_reader, 1):
                    if not row or not row[0].strip():
                        continue
                    
                    word_info = self._parse_row(row, format_info['detected_format'], language_hint)
                    if word_info:
                        word_info['source'] = csv_path.stem
                        word_info['dataset'] = csv_path.name
                        words_data.append(word_info)
        
        except Exception as e:
            print(f"❌ Error loading {csv_path.name}: {e}")
            return []
        
        print(f"📊 Loaded {len(words_data)} words from {csv_path.name}")
        return words_data
    
    def _parse_row(self, row: List[str], format_type: str, language_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Parse a CSV row based on detected format."""
        if not row or not row[0].strip():
            return None
        
        word = row[0].strip().lower()
        
        # Standard format parsing
        if format_type == 'word_meaning_severity' and len(row) >= 3:
            return {
                'word': word,
                'meaning': row[1].strip() if len(row) > 1 else '',
                'severity': int(row[2].strip()) if len(row) > 2 and self._is_numeric(row[2]) else 5,
                'language': language_hint or self._detect_language(word),
                'confidence': 1.0
            }
        
        elif format_type == 'word_category' and len(row) >= 2:
            return {
                'word': word,
                'meaning': row[1].strip(),
                'severity': self._estimate_severity(word, row[1].strip()),
                'language': language_hint or self._detect_language(word),
                'confidence': 0.8
            }
        
        elif format_type == 'simple_wordlist':
            return {
                'word': word,
                'meaning': '',
                'severity': 5,  # Default severity
                'language': language_hint or self._detect_language(word),
                'confidence': 0.7
            }
        
        else:  # custom_format - do our best
            return {
                'word': word,
                'meaning': row[1].strip() if len(row) > 1 else '',
                'severity': 5,
                'language': language_hint or self._detect_language(word),
                'confidence': 0.6
            }
    
    def _detect_language(self, word: str) -> str:
        """Attempt to detect language of a word."""
        # Simple heuristics for language detection
        if any(char in word for char in 'आईउएओअकखगघचछजझटठडढतथदधनपफबभमयरलवशषसह'):
            return 'hindi_devanagari'
        elif any(char in word for char in 'اردوہےکیںمیںنےکوہیںکہسےجوبھیتھاتھیپرایکاسکاکیکرگیئے'):
            return 'urdu'
        elif any(char in 'abcdefghijklmnopqrstuvwxyz' for char in word) and any(char in 'aeiou' for char in word) and len(word) > 3:
            # Check if it might be transliterated Hindi/Hinglish
            hinglish_patterns = ['ch', 'bh', 'dh', 'gh', 'kh', 'ph', 'th', 'aa', 'ee', 'oo']
            if any(pattern in word for pattern in hinglish_patterns):
                return 'hinglish'
            return 'english'
        else:
            return 'unknown'
    
    def _estimate_severity(self, word: str, meaning: str) -> int:
        """Estimate severity based on word and meaning."""
        severe_indicators = ['fuck', 'motherfucker', 'cunt', 'extreme', 'severe']
        moderate_indicators = ['damn', 'hell', 'bitch', 'bastard', 'ass']
        mild_indicators = ['idiot', 'stupid', 'fool', 'silly']
        
        text = f"{word} {meaning}".lower()
        
        if any(indicator in text for indicator in severe_indicators):
            return 8
        elif any(indicator in text for indicator in moderate_indicators):
            return 6
        elif any(indicator in text for indicator in mild_indicators):
            return 3
        else:
            return 5
    
    def find_csv_files(self, directory: Optional[Path] = None) -> List[Path]:
        """Find all CSV files in directory and subdirectories."""
        search_dir = directory or self.data_dir
        
        csv_files = []
        
        # Search in common locations
        search_patterns = [
            str(search_dir / "*.csv"),
            str(search_dir / "**/*.csv"),
            str(search_dir / "data/*.csv"),
            str(search_dir / "datasets/*.csv"),
            str(search_dir / "wordlists/*.csv"),
            str(search_dir.parent / "*.csv"),  # Also search parent directory
        ]
        
        for pattern in search_patterns:
            csv_files.extend(glob.glob(pattern, recursive=True))
        
        # Remove duplicates and return as Path objects
        unique_files = list(set(csv_files))
        return [Path(f) for f in unique_files]
    
    def train_all_datasets(self, auto_discover: bool = True, csv_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train with all available CSV datasets.
        
        Args:
            auto_discover: Whether to automatically find CSV files
            csv_files: Specific list of CSV files to process
            
        Returns:
            Training results summary
        """
        print("🚀 UNIVERSAL PROFANITY TRAINING SYSTEM")
        print("=" * 60)
        
        # Find CSV files
        if csv_files:
            csv_paths = [Path(f) for f in csv_files]
        elif auto_discover:
            csv_paths = self.find_csv_files()
        else:
            csv_paths = []
        
        if not csv_paths:
            print("❌ No CSV files found to train with")
            return {'success': False, 'error': 'No CSV files found'}
        
        print(f"📂 Found {len(csv_paths)} CSV file(s) to process:")
        for path in csv_paths:
            print(f"   • {path}")
        
        # Load and process all datasets
        all_words_data = []
        dataset_stats = {}
        
        for csv_path in csv_paths:
            words_data = self.load_csv_dataset(csv_path)
            if words_data:
                all_words_data.extend(words_data)
                dataset_stats[csv_path.name] = {
                    'word_count': len(words_data),
                    'languages': list(set(w['language'] for w in words_data))
                }
                self.trained_datasets.append(csv_path.name)
        
        if not all_words_data:
            print("❌ No words loaded from any dataset")
            return {'success': False, 'error': 'No words loaded'}
        
        print(f"\n📊 Total words loaded: {len(all_words_data)}")
        
        # Group by language and add to detection system
        language_groups = {}
        for word_info in all_words_data:
            lang = word_info['language']
            if lang not in language_groups:
                language_groups[lang] = []
            language_groups[lang].append(word_info['word'])
        
        # Add to profanity detection system
        for language, words in language_groups.items():
            if language != 'unknown':
                add_language_support(language, words)
                add_custom_profanity_words(words, 'hindi_latin')  # Also add to main Hindi detection
                print(f"🌐 Added {len(words)} words for language: {language}")
        
        # Save to learned words
        self._save_learned_words(all_words_data)
        
        # Test the training
        test_results = self._run_tests()
        
        return {
            'success': True,
            'total_words': len(all_words_data),
            'datasets_processed': len(self.trained_datasets),
            'dataset_stats': dataset_stats,
            'language_groups': {k: len(v) for k, v in language_groups.items()},
            'test_results': test_results,
            'supported_languages': list(PROFANITY_PATTERNS.keys())
        }
    
    def _save_learned_words(self, words_data: List[Dict[str, Any]]):
        """Save all words to learned words file."""
        # Load existing learned words
        learned_words = {}
        if self.learned_words_path.exists():
            try:
                with open(self.learned_words_path, 'r', encoding='utf-8') as f:
                    learned_words = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading existing learned words: {e}")
        
        # Group by language
        for word_info in words_data:
            lang = word_info['language']
            if lang not in learned_words:
                learned_words[lang] = []
            
            # Check if word already exists
            existing = any(
                isinstance(item, dict) and item.get('word') == word_info['word'] 
                for item in learned_words[lang]
            )
            
            if not existing:
                learned_words[lang].append({
                    'word': word_info['word'],
                    'meaning': word_info['meaning'],
                    'severity': word_info['severity'],
                    'source': word_info['source'],
                    'dataset': word_info['dataset'],
                    'confidence': word_info['confidence']
                })
        
        # Save updated learned words
        self.learned_words_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.learned_words_path, 'w', encoding='utf-8') as f:
            json.dump(learned_words, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved learned words to: {self.learned_words_path}")
    
    def _run_tests(self) -> List[Dict[str, Any]]:
        """Run detection tests on common profane words."""
        test_words = [
            'chutiya', 'madarchod', 'bhenchod', 'gandu', 'randi', 'saala',
            'fuck', 'shit', 'bitch', 'bastard', 'damn'
        ]
        
        test_results = []
        for word in test_words:
            result = test_profanity_detection(word)
            test_results.append({
                'word': word,
                'detected': len(result['detected_words']) > 0
            })
        
        return test_results
    
    def generate_report(self, results: Dict[str, Any], output_path: Optional[str] = None):
        """Generate comprehensive training report."""
        if not results['success']:
            print(f"❌ Training failed: {results.get('error', 'Unknown error')}")
            return
        
        report = f"""
🎯 UNIVERSAL PROFANITY TRAINING REPORT
{'=' * 60}

✅ Training Status: SUCCESS
📊 Total Words Processed: {results['total_words']}
📂 Datasets Processed: {results['datasets_processed']}

📈 DATASET BREAKDOWN:
{'-' * 30}
"""
        
        for dataset, stats in results['dataset_stats'].items():
            report += f"• {dataset}: {stats['word_count']} words ({', '.join(stats['languages'])})\n"
        
        report += f"""
🌐 LANGUAGE DISTRIBUTION:
{'-' * 25}
"""
        
        for lang, count in results['language_groups'].items():
            report += f"• {lang}: {count} words\n"
        
        report += f"""
🧪 DETECTION TESTS:
{'-' * 20}
"""
        
        for test in results['test_results']:
            status = "✅ DETECTED" if test['detected'] else "❌ MISSED"
            report += f"• {test['word']}: {status}\n"
        
        report += f"""
🔧 SUPPORTED LANGUAGES:
{'-' * 25}
{', '.join(results['supported_languages'])}

📝 SYSTEM STATUS:
{'-' * 17}
• Auto-discovery: ✅ Enabled
• Multi-format support: ✅ Enabled  
• Multi-language support: ✅ Enabled
• Real-time training: ✅ Ready

🚀 USAGE:
{'-' * 10}
• Add any CSV file to your project directory
• Run: python3 universal_trainer.py
• System will automatically detect and train with all CSV files
• Supports multiple formats and languages automatically

"""
        
        print(report)
        
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"💾 Report saved to: {output_path}")
            except Exception as e:
                print(f"⚠️ Failed to save report: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='Universal Profanity Training System')
    parser.add_argument('--csv-files', nargs='*', help='Specific CSV files to process')
    parser.add_argument('--data-dir', help='Directory to scan for CSV files')
    parser.add_argument('--no-auto-discover', action='store_true', help='Disable automatic CSV discovery')
    parser.add_argument('--report', default='universal_training_report.txt', help='Output report file')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = UniversalTrainer(args.data_dir)
    
    # Train with datasets
    results = trainer.train_all_datasets(
        auto_discover=not args.no_auto_discover,
        csv_files=args.csv_files
    )
    
    # Generate report
    trainer.generate_report(results, args.report)
    
    if results['success']:
        print("\n🎉 UNIVERSAL TRAINING COMPLETED!")
        print("Your profanity detection system is now enhanced with all available datasets.")
        print("🔥 Just add any CSV file and run this script again to train automatically!")
    else:
        print(f"\n❌ Training failed: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
