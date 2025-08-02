"""
Production-ready regex-based profanity scanner for multilingual content.
Optimized for Whisper transcript processing with cached patterns and fast scanning.
"""

import re
import json
import os
import unicodedata
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ProfanityScanner:
    """
    High-performance regex-based profanity scanner with multilingual support.
    Designed for production use with Whisper transcript processing.
    """
    
    def __init__(self, learned_words_path: Optional[str] = None):
        """
        Initialize the profanity scanner.
        
        Args:
            learned_words_path: Path to learned_words.json file
        """
        self.learned_words_path = learned_words_path or self._get_default_wordlist_path()
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        self.word_mappings: Dict[str, Set[str]] = {}
        self.is_loaded = False
        
        # Performance optimization: precompile normalization mapping
        self.normalization_map = str.maketrans({
            '@': 'a', '$': 's', '3': 'e', '1': 'i', '0': 'o',
            '4': 'a', '5': 's', '7': 't', '8': 'b', '#': '',
            '*': '', '+': '', '!': 'i', '€': 'e', '£': 'l'
        })
        
        # Load patterns on initialization
        self.load_profanity_patterns()
    
    def _get_default_wordlist_path(self) -> str:
        """Get default path for learned_words.json"""
        backend_dir = Path(__file__).parent.parent
        return str(backend_dir / "data" / "wordlists" / "learned_words.json")
    
    def _normalize_text(self, text: str) -> str:
        """
        Fast text normalization for profanity detection.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text ready for pattern matching
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove diacritics using Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Apply character substitutions
        text = text.translate(self.normalization_map)
        
        # Remove excessive whitespace and punctuation
        text = re.sub(r'[^\w\s\u0900-\u097F\u0600-\u06FF]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _create_word_variations(self, word: str) -> Set[str]:
        """
        Generate variations of a word for comprehensive matching.
        
        Args:
            word: Base word to create variations for
            
        Returns:
            Set of word variations
        """
        variations = {word.lower()}
        
        # Add normalized version
        normalized = self._normalize_text(word)
        if normalized:
            variations.add(normalized)
        
        # Add space-removed version
        variations.add(word.replace(' ', ''))
        
        # Add common separator variations
        for sep in ['_', '-', '.']:
            variations.add(word.replace(' ', sep))
        
        # Add leetspeak variations
        leetspeak = {
            'a': ['@', '4'], 'e': ['3', '€'], 'i': ['1', '!'], 
            'o': ['0'], 's': ['$', '5'], 't': ['7'], 'b': ['8']
        }
        
        for char, replacements in leetspeak.items():
            if char in word.lower():
                for replacement in replacements:
                    variations.add(word.lower().replace(char, replacement))
        
        return variations
    
    def _build_regex_pattern(self, words: List[str]) -> re.Pattern:
        """
        Build optimized regex pattern from word list.
        
        Args:
            words: List of profane words
            
        Returns:
            Compiled regex pattern
        """
        if not words:
            return re.compile(r'(?!)', re.IGNORECASE | re.UNICODE)
        
        # Create all variations
        all_variations = set()
        for word in words:
            variations = self._create_word_variations(word)
            all_variations.update(variations)
        
        # Remove empty strings and sort by length (longest first for better matching)
        valid_words = [w for w in all_variations if w and len(w) > 1]
        valid_words.sort(key=len, reverse=True)
        
        # Escape special regex characters
        escaped_words = [re.escape(word) for word in valid_words]
        
        # Build word boundary pattern for better accuracy
        pattern_parts = []
        for word in escaped_words:
            # Use word boundaries for Latin script, flexible boundaries for other scripts
            if re.match(r'^[a-zA-Z]', word):
                pattern_parts.append(rf'\b{word}\b')
            else:
                pattern_parts.append(word)
        
        # Combine with OR operator
        pattern_str = '|'.join(pattern_parts)
        
        try:
            return re.compile(pattern_str, re.IGNORECASE | re.UNICODE)
        except re.error as e:
            logger.error(f"Regex compilation error: {e}")
            return re.compile(r'(?!)', re.IGNORECASE | re.UNICODE)
    
    def load_profanity_patterns(self) -> bool:
        """
        Load and compile profanity patterns from learned_words.json.
        
        Returns:
            True if patterns loaded successfully, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(self.learned_words_path):
                logger.warning(f"Learned words file not found: {self.learned_words_path}")
                self._create_default_wordlist()
            
            # Load word data
            with open(self.learned_words_path, 'r', encoding='utf-8') as f:
                word_data = json.load(f)
            
            # Compile patterns for each language
            self.compiled_patterns.clear()
            self.word_mappings.clear()
            
            total_words = 0
            for language, words in word_data.items():
                if not isinstance(words, list):
                    continue
                
                # Extract word strings from different formats
                word_list = []
                for item in words:
                    if isinstance(item, str):
                        word_list.append(item)
                    elif isinstance(item, dict) and 'word' in item:
                        word_list.append(item['word'])
                
                if word_list:
                    # Compile regex pattern
                    self.compiled_patterns[language] = self._build_regex_pattern(word_list)
                    
                    # Store word mappings for reference
                    self.word_mappings[language] = set(word_list)
                    
                    total_words += len(word_list)
                    logger.info(f"Loaded {len(word_list)} {language} profanity patterns")
            
            self.is_loaded = True
            logger.info(f"Successfully loaded {total_words} profanity patterns across {len(self.compiled_patterns)} languages")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load profanity patterns: {e}")
            self.is_loaded = False
            return False
    
    def _create_default_wordlist(self):
        """Create a default learned_words.json file if it doesn't exist."""
        default_data = {
            "english": [
                "fuck", "shit", "bitch", "asshole", "damn", "bastard",
                "motherfucker", "cocksucker", "dickhead", "cunt"
            ],
            "hindi": [
                "chutiya", "madarchod", "bhenchod", "bhosadike", "randi",
                "harami", "gandu", "lund", "chut", "gaand", "kamina",
                "saala", "kutti", "chu", "bc", "mc", "bkl",
                "bhen ki chut", "ma ki chut", "behen ki chut"
            ],
            "hinglish": [
                "bc", "mc", "bkl", "wtf", "stfu", "gtfo"
            ]
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.learned_words_path), exist_ok=True)
        
        # Save default wordlist
        with open(self.learned_words_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created default wordlist at {self.learned_words_path}")
    
    def is_abusive(self, text: str) -> bool:
        """
        Check if text contains profanity.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains profanity, False otherwise
        """
        if not self.is_loaded or not text:
            return False
        
        normalized_text = self._normalize_text(text)
        
        # Check against all language patterns
        for pattern in self.compiled_patterns.values():
            if pattern.search(normalized_text):
                return True
        
        return False
    
    def find_profanity_matches(self, text: str) -> List[Dict[str, str]]:
        """
        Find all profanity matches in text with details.
        
        Args:
            text: Text to scan
            
        Returns:
            List of dictionaries with match details
        """
        if not self.is_loaded or not text:
            return []
        
        matches = []
        normalized_text = self._normalize_text(text)
        
        for language, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(normalized_text):
                matches.append({
                    'word': match.group(),
                    'language': language,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        # Remove duplicates and sort by position
        unique_matches = []
        seen_positions = set()
        
        for match in sorted(matches, key=lambda x: x['start_pos']):
            pos_key = (match['start_pos'], match['end_pos'])
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_matches.append(match)
        
        return unique_matches
    
    def scan_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Scan Whisper transcript segments for profanity.
        
        Args:
            segments: List of Whisper transcript segments
            
        Returns:
            List of segments containing profanity with timing and match details
        """
        if not self.is_loaded:
            logger.warning("Profanity patterns not loaded. Call load_profanity_patterns() first.")
            return []
        
        abusive_segments = []
        
        for segment in segments:
            if not isinstance(segment, dict) or 'text' not in segment:
                continue
            
            text = segment.get('text', '').strip()
            if not text:
                continue
            
            # Find profanity matches
            matches = self.find_profanity_matches(text)
            
            if matches:
                # Create abusive segment entry
                abusive_segment = {
                    'text': text,
                    'start': segment.get('start', 0.0),
                    'end': segment.get('end', 0.0),
                    'profane_words': [match['word'] for match in matches],
                    'languages': list(set(match['language'] for match in matches)),
                    'matches': matches,
                    'match_count': len(matches)
                }
                
                abusive_segments.append(abusive_segment)
        
        # Sort by start time
        abusive_segments.sort(key=lambda x: x['start'])
        
        logger.info(f"Found {len(abusive_segments)} segments with profanity out of {len(segments)} total segments")
        
        return abusive_segments
    
    def add_words(self, words: List[str], language: str = 'custom') -> bool:
        """
        Add new words to the profanity database.
        
        Args:
            words: List of words to add
            language: Language category
            
        Returns:
            True if words added successfully
        """
        try:
            # Load existing data
            if os.path.exists(self.learned_words_path):
                with open(self.learned_words_path, 'r', encoding='utf-8') as f:
                    word_data = json.load(f)
            else:
                word_data = {}
            
            # Add new words
            if language not in word_data:
                word_data[language] = []
            
            # Convert to consistent format
            for word in words:
                if word not in word_data[language]:
                    word_data[language].append(word)
            
            # Save updated data
            with open(self.learned_words_path, 'w', encoding='utf-8') as f:
                json.dump(word_data, f, indent=2, ensure_ascii=False)
            
            # Reload patterns
            self.load_profanity_patterns()
            
            logger.info(f"Added {len(words)} words to {language} category")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add words: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about loaded patterns.
        
        Returns:
            Dictionary with pattern statistics
        """
        if not self.is_loaded:
            return {'total_languages': 0, 'total_words': 0}
        
        stats = {
            'total_languages': len(self.word_mappings),
            'total_words': sum(len(words) for words in self.word_mappings.values())
        }
        
        for language, words in self.word_mappings.items():
            stats[f'{language}_words'] = len(words)
        
        return stats


# Global scanner instance for performance
_global_scanner: Optional[ProfanityScanner] = None


def get_scanner(learned_words_path: Optional[str] = None) -> ProfanityScanner:
    """
    Get global profanity scanner instance.
    
    Args:
        learned_words_path: Optional path to wordlist file
        
    Returns:
        ProfanityScanner instance
    """
    global _global_scanner
    
    if _global_scanner is None:
        _global_scanner = ProfanityScanner(learned_words_path)
    
    return _global_scanner


def load_profanity_patterns(learned_words_path: Optional[str] = None) -> bool:
    """
    Load profanity patterns into global scanner.
    
    Args:
        learned_words_path: Optional path to wordlist file
        
    Returns:
        True if patterns loaded successfully
    """
    scanner = get_scanner(learned_words_path)
    return scanner.load_profanity_patterns()


def is_abusive(text: str) -> bool:
    """
    Check if text contains profanity using global scanner.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains profanity
    """
    scanner = get_scanner()
    return scanner.is_abusive(text)


def scan_segments(segments: List[Dict]) -> List[Dict]:
    """
    Scan Whisper transcript segments for profanity using global scanner.
    
    Args:
        segments: List of Whisper transcript segments
        
    Returns:
        List of segments containing profanity
    """
    scanner = get_scanner()
    return scanner.scan_segments(segments)


def find_profanity_matches(text: str) -> List[Dict[str, str]]:
    """
    Find all profanity matches in text using global scanner.
    
    Args:
        text: Text to scan
        
    Returns:
        List of match details
    """
    scanner = get_scanner()
    return scanner.find_profanity_matches(text)


def add_words(words: List[str], language: str = 'custom') -> bool:
    """
    Add new words to profanity database using global scanner.
    
    Args:
        words: List of words to add
        language: Language category
        
    Returns:
        True if words added successfully
    """
    scanner = get_scanner()
    return scanner.add_words(words, language)


def get_statistics() -> Dict[str, int]:
    """
    Get profanity scanner statistics.
    
    Returns:
        Dictionary with statistics
    """
    scanner = get_scanner()
    return scanner.get_statistics()


# Initialize on import for production use
if __name__ != "__main__":
    load_profanity_patterns()
