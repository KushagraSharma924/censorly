#!/usr/bin/env python3
"""
Test script for ai-profanity-filter components
Tests individual modules to ensure they work correctly.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from censor_utils import test_profanity_detection, initialize_profanity_filter
    print("✅ censor_utils imported successfully")
    CENSOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing censor_utils: {e}")
    CENSOR_AVAILABLE = False

try:
    from whisper_transcribe import format_timestamp
    print("✅ whisper_transcribe imported successfully") 
except ImportError as e:
    print(f"❌ Error importing whisper_transcribe: {e}")

try:
    from audio_utils import validate_video_file
    print("✅ audio_utils imported successfully")
except ImportError as e:
    print(f"❌ Error importing audio_utils: {e}")

# Test profanity detection
if CENSOR_AVAILABLE:
    print("\n🧪 Testing profanity detection...")
    test_texts = [
        "Hello world, this is a clean sentence.",
        "This contains a damn bad word.",
        "What the hell is going on here?",
        "This is completely fine text."
    ]

    initialize_profanity_filter()
    for text in test_texts:
        result = test_profanity_detection(text)
        print(f"Text: '{text}'")
        print(f"  Contains profanity: {result['contains_profanity']}")
        print(f"  Censored: '{result['censored_text']}'")
        print(f"  Detected words: {result['detected_words']}")
        print()
else:
    print("\n⚠️  Skipping profanity detection test (censor_utils not available)")

# Test timestamp formatting
print("🧪 Testing timestamp formatting...")
test_times = [65.5, 125.75, 3661.25]
for time in test_times:
    formatted = format_timestamp(time)
    print(f"  {time}s -> {formatted}")

print("\n✅ All tests completed!")
print("\n📋 To use ai-profanity-filter:")
print("   python main.py <video_file> [--output output_name.mp4]")
print("   Example: python main.py sample_video.mp4 --output clean_video.mp4")
