#!/usr/bin/env python3
"""
Test script for multilingual profanity detection
Demonstrates detection of English, Hindi (Latin), and Hindi (Devanagari) profanity
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / 'backend'))

from modules.detect_words import (
    test_profanity_detection, 
    get_statistics, 
    get_supported_languages,
    add_custom_profanity_words,
    add_language_support
)

def test_multilingual_detection():
    """Test profanity detection across multiple languages"""
    
    print("🧪 Testing Multilingual Profanity Detection")
    print("=" * 50)
    
    # Test cases with different languages and scripts
    test_cases = [
        # English profanity
        "This is fucking terrible shit",
        "You are such a bitch and asshole",
        
        # Hindi profanity in Latin script
        "Tu chutiya hai yaar",
        "Madarchod kya kar raha hai",
        "Bhenchod this is annoying",
        "Saala kya problem hai",
        
        # Hindi profanity in Devanagari script
        "तू चुतिया है यार",
        "मादरचोद क्या कर रहा है",
        "भेनचोद this is mixed script",
        "साला क्या प्रॉब्लम है",
        
        # Mixed language profanity
        "This fucking चुतिया is annoying",
        "What a madarchod behavior यार",
        "Stop being such a bitch साला",
        
        # Clean text (should not detect anything)
        "This is a normal conversation",
        "मैं आपसे मिलकर खुश हूं",
        "How are you doing today my friend",
        
        # Edge cases with variations
        "ch00tiya hai ye",  # Numbers as letters
        "madarch0d behavior",  # Mixed characters
        "bh3nch0d what is this",  # Leetspeak
        "mc bc kya hai ye",  # Abbreviations
    ]
    
    print(f"📝 Testing {len(test_cases)} test cases...\n")
    
    total_detections = 0
    
    for i, text in enumerate(test_cases, 1):
        print(f"Test {i}: \"{text}\"")
        result = test_profanity_detection(text)
        
        if result['contains_profanity']:
            print(f"   ✅ DETECTED ({result['total_detections']} words)")
            for detection in result['detected_words']:
                lang_name = {
                    'english': 'English',
                    'hindi_latin': 'Hindi (Latin)',
                    'hindi_devanagari': 'Hindi (Devanagari)'
                }.get(detection['language'], detection['language'])
                print(f"      - '{detection['word']}' [{lang_name}]")
            print(f"   Languages: {', '.join(result['languages_detected'])}")
            total_detections += result['total_detections']
        else:
            print("   ❌ CLEAN (no profanity detected)")
        
        print()
    
    print(f"📊 Summary: {total_detections} total profanity detections across all test cases")


def test_transcript_simulation():
    """Test with simulated Whisper transcript data"""
    
    print("\n🎙️ Testing with Simulated Transcript Data")
    print("=" * 50)
    
    # Simulate Whisper transcript format
    simulated_transcript = {
        'text': 'This fucking chutiya is being a मादरचोद and acting like a bitch साला',
        'segments': [
            {
                'start': 0.0,
                'end': 2.5,
                'text': 'This fucking chutiya is being a',
                'words': [
                    {'word': 'This', 'start': 0.0, 'end': 0.5},
                    {'word': 'fucking', 'start': 0.5, 'end': 1.0},
                    {'word': 'chutiya', 'start': 1.0, 'end': 1.5},
                    {'word': 'is', 'start': 1.5, 'end': 1.7},
                    {'word': 'being', 'start': 1.7, 'end': 2.0},
                    {'word': 'a', 'start': 2.0, 'end': 2.1}
                ]
            },
            {
                'start': 2.5,
                'end': 5.0,
                'text': 'मादरचोद and acting like a',
                'words': [
                    {'word': 'मादरचोद', 'start': 2.5, 'end': 3.0},
                    {'word': 'and', 'start': 3.0, 'end': 3.2},
                    {'word': 'acting', 'start': 3.2, 'end': 3.7},
                    {'word': 'like', 'start': 3.7, 'end': 3.9},
                    {'word': 'a', 'start': 3.9, 'end': 4.0}
                ]
            },
            {
                'start': 5.0,
                'end': 7.0,
                'text': 'bitch साला',
                'words': [
                    {'word': 'bitch', 'start': 5.0, 'end': 5.5},
                    {'word': 'साला', 'start': 5.5, 'end': 6.0}
                ]
            }
        ]
    }
    
    # Import the main detection function
    from modules.detect_words import detect_abusive_words
    
    # Test the detection
    detected_segments = detect_abusive_words(simulated_transcript)
    
    print(f"📹 Original transcript: \"{simulated_transcript['text']}\"")
    print(f"🔍 Detected {len(detected_segments)} profane segments:")
    
    for segment in detected_segments:
        duration = segment['end'] - segment['start']
        lang_names = []
        for lang in segment['languages']:
            lang_name = {
                'english': 'English',
                'hindi_latin': 'Hindi (Latin)',
                'hindi_devanagari': 'Hindi (Devanagari)'
            }.get(lang, lang)
            lang_names.append(lang_name)
        
        print(f"   ⏱️  {segment['start']:.1f}s-{segment['end']:.1f}s ({duration:.1f}s)")
        print(f"      Text: \"{segment['text']}\"")
        print(f"      Words: {segment['profane_words']}")
        print(f"      Languages: {', '.join(lang_names)}")
        print(f"      Type: {segment['type']}")
        print()


def test_custom_words():
    """Test adding custom profanity words"""
    
    print("\n🛠️ Testing Custom Word Addition")
    print("=" * 50)
    
    # Add some custom words
    custom_english = ["dummy", "test_word"]
    custom_hindi = ["बकवास", "test_hindi"]
    
    print("📝 Adding custom words...")
    add_custom_profanity_words(custom_english, 'english')
    add_custom_profanity_words(custom_hindi, 'hindi_latin')
    
    # Test detection with custom words
    test_texts = [
        "This is a dummy text",
        "Stop saying test_word",
        "यह बकवास है",
        "test_hindi behavior"
    ]
    
    for text in test_texts:
        result = test_profanity_detection(text)
        status = "DETECTED" if result['contains_profanity'] else "CLEAN"
        print(f"   \"{text}\" → {status}")


def test_new_language():
    """Test adding support for a new language"""
    
    print("\n🌐 Testing New Language Support")
    print("=" * 50)
    
    # Add support for Punjabi (example)
    punjabi_words = ["khotya", "gadha", "kameena"]
    add_language_support('punjabi', punjabi_words)
    
    # Test detection
    result = test_profanity_detection("Tu khotya hai gadha")
    print(f"Punjabi test: \"Tu khotya hai gadha\"")
    if result['contains_profanity']:
        print(f"   ✅ DETECTED: {result['detected_words']}")
    else:
        print("   ❌ NOT DETECTED")


def show_statistics():
    """Show detection statistics"""
    
    print("\n📊 Detection Statistics")
    print("=" * 50)
    
    stats = get_statistics()
    supported_langs = get_supported_languages()
    
    print(f"🌐 Supported Languages: {stats['total_languages']}")
    for lang_name, count in stats['languages'].items():
        print(f"   - {lang_name}: {count} patterns")
    
    print(f"\n📝 Total Patterns: {stats['total_patterns']}")
    print(f"🔤 Language Codes: {', '.join(supported_langs)}")


def main():
    """Run all tests"""
    
    print("🧪 Multilingual Profanity Detection Test Suite")
    print("🎯 Testing English, Hindi (Latin & Devanagari) Detection")
    print("=" * 60)
    
    try:
        # Show initial statistics
        show_statistics()
        
        # Run basic detection tests
        test_multilingual_detection()
        
        # Test with transcript format
        test_transcript_simulation()
        
        # Test custom word addition
        test_custom_words()
        
        # Test new language support
        test_new_language()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📝 Next Steps:")
        print("1. The system now supports multilingual profanity detection")
        print("2. Use detect_abusive_words() with Whisper transcript data")
        print("3. Add more languages using add_language_support()")
        print("4. Customize word lists using add_custom_profanity_words()")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
