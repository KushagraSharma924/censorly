#!/usr/bin/env python3
"""
Word List Analysis for MovieCensorAI
Demonstrates how the profanity word list is created and managed.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from better_profanity import profanity
from censor_utils import initialize_profanity_filter, add_custom_profanity_words, test_profanity_detection


def analyze_wordlist():
    """Analyze the built-in profanity word list."""
    print("🔍 MovieCensorAI - Word List Analysis")
    print("=" * 50)
    
    # Initialize the profanity filter
    print("📚 Loading built-in profanity word list...")
    initialize_profanity_filter()
    
    # Get word list details
    wordset = profanity.CENSOR_WORDSET
    words = [str(word) for word in wordset]
    words.sort()
    
    print(f"✅ Built-in word list loaded successfully!")
    print(f"📊 Total words in database: {len(words)}")
    
    # Show word categories
    print("\n📂 Word Categories (samples):")
    print("   • Basic profanity:", [w for w in words if len(w) <= 5][:10])
    print("   • Slang terms:", [w for w in words if 6 <= len(w) <= 10][:10])
    print("   • Phrases:", [w for w in words if len(w) > 10][:5])
    
    return words


def demonstrate_detection():
    """Demonstrate profanity detection with examples."""
    print("\n🧪 Testing Profanity Detection")
    print("-" * 30)
    
    test_texts = [
        "This is a clean sentence.",
        "This is a damn good example.",
        "What the hell is happening?",
        "Holy shit, that's crazy!",
        "You're being a real asshole.",
        "That's fucking awesome!"
    ]
    
    for text in test_texts:
        result = test_profanity_detection(text)
        status = "🚫 PROFANE" if result['contains_profanity'] else "✅ CLEAN"
        print(f"\n{status} '{text}'")
        if result['detected_words']:
            print(f"         Detected: {result['detected_words']}")
            print(f"         Censored: '{result['censored_text']}'")


def demonstrate_custom_words():
    """Show how to add custom words to the filter."""
    print("\n🛠️  Adding Custom Words")
    print("-" * 25)
    
    # Test before adding custom words
    test_text = "You're such a noob at this game!"
    print(f"Original text: '{test_text}'")
    
    result_before = test_profanity_detection(test_text)
    print(f"Before custom words: {result_before['contains_profanity']} - {result_before['detected_words']}")
    
    # Add custom words
    custom_words = ["noob", "scrub", "tryhard"]
    print(f"\n➕ Adding custom words: {custom_words}")
    add_custom_profanity_words(custom_words)
    
    result_after = test_profanity_detection(test_text)
    print(f"After custom words: {result_after['contains_profanity']} - {result_after['detected_words']}")
    print(f"Censored version: '{result_after['censored_text']}'")


def show_wordlist_sources():
    """Explain where the word list comes from."""
    print("\n📖 Word List Sources & Creation")
    print("=" * 40)
    
    print("""
🔍 How the Word List is Created:

1. **Built-in Database**: 
   • The 'better-profanity' library comes with 916 pre-defined profane words
   • These include common swear words, slurs, and offensive terms
   • Words are stored as VaryingString objects for flexibility

2. **Categories Included**:
   • Basic profanity (4-letter words, etc.)
   • Sexual terms and slurs
   • Racist and discriminatory language
   • Internet slang and abbreviations
   • Multi-word phrases

3. **Dynamic Addition**:
   • You can add custom words using add_custom_profanity_words()
   • Words are added to the existing filter at runtime
   • Custom words persist for the session

4. **Word Processing**:
   • Words are checked after removing punctuation
   • Case-insensitive matching
   • Handles variations and misspellings

5. **In MovieCensorAI**:
   • initialize_profanity_filter() loads the default list
   • detect_profane_words() processes each word individually
   • Word-level timestamps ensure precise censoring
    """)


def show_word_samples():
    """Show actual word samples (safely)."""
    print("\n📝 Word List Samples")
    print("-" * 20)
    
    words = [str(word) for word in profanity.CENSOR_WORDSET]
    words.sort()
    
    # Show safe examples
    safe_examples = [w for w in words if w in ['damn', 'hell', 'crap', 'stupid', 'idiot']]
    print(f"Safe examples: {safe_examples[:10]}")
    
    # Show word lengths distribution
    lengths = {}
    for word in words:
        length = len(word)
        lengths[length] = lengths.get(length, 0) + 1
    
    print(f"\n📊 Word Length Distribution:")
    for length in sorted(lengths.keys())[:10]:
        print(f"   {length} letters: {lengths[length]} words")


def main():
    """Main function to demonstrate word list functionality."""
    try:
        # Analyze the built-in word list
        analyze_wordlist()
        
        # Show how words are detected
        demonstrate_detection()
        
        # Show custom word addition
        demonstrate_custom_words()
        
        # Explain word list sources
        show_wordlist_sources()
        
        # Show word samples
        show_word_samples()
        
        print("\n🎯 Summary:")
        print("• Built-in: 916 profane words from better-profanity")
        print("• Customizable: Add your own words with add_custom_profanity_words()")
        print("• Smart matching: Handles punctuation and case variations")
        print("• Precise targeting: Word-level timestamps for exact censoring")
        
    except Exception as e:
        print(f"❌ Error during word list analysis: {e}")


if __name__ == "__main__":
    main()
