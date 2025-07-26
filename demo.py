#!/usr/bin/env python3
"""
Demo script for ai-profanity-filter
Creates a sample audio file with simulated speech to demonstrate the censoring capability.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def create_demo_transcript():
    """Create a demo transcript with profanity for testing."""
    return {
        'text': 'Hello this is a test. This is a damn good example. What the hell is happening? This is fine.',
        'segments': [
            {
                'text': ' Hello this is a test.',
                'start': 0.0,
                'end': 2.5,
                'words': [
                    {'word': 'Hello', 'start': 0.0, 'end': 0.5},
                    {'word': 'this', 'start': 0.6, 'end': 0.8},
                    {'word': 'is', 'start': 0.9, 'end': 1.0},
                    {'word': 'a', 'start': 1.1, 'end': 1.2},
                    {'word': 'test.', 'start': 1.3, 'end': 2.5}
                ]
            },
            {
                'text': ' This is a damn good example.',
                'start': 3.0,
                'end': 6.0,
                'words': [
                    {'word': 'This', 'start': 3.0, 'end': 3.3},
                    {'word': 'is', 'start': 3.4, 'end': 3.5},
                    {'word': 'a', 'start': 3.6, 'end': 3.7},
                    {'word': 'damn', 'start': 3.8, 'end': 4.2},
                    {'word': 'good', 'start': 4.3, 'end': 4.6},
                    {'word': 'example.', 'start': 4.7, 'end': 6.0}
                ]
            },
            {
                'text': ' What the hell is happening?',
                'start': 6.5,
                'end': 9.0,
                'words': [
                    {'word': 'What', 'start': 6.5, 'end': 6.8},
                    {'word': 'the', 'start': 6.9, 'end': 7.0},
                    {'word': 'hell', 'start': 7.1, 'end': 7.5},
                    {'word': 'is', 'start': 7.6, 'end': 7.7},
                    {'word': 'happening?', 'start': 7.8, 'end': 9.0}
                ]
            },
            {
                'text': ' This is fine.',
                'start': 9.5,
                'end': 11.0,
                'words': [
                    {'word': 'This', 'start': 9.5, 'end': 9.7},
                    {'word': 'is', 'start': 9.8, 'end': 9.9},
                    {'word': 'fine.', 'start': 10.0, 'end': 11.0}
                ]
            }
        ]
    }

def main():
    """Run the demo to show profanity detection capabilities."""
    print("🎬 ai-profanity-filter Demo")
    print("=" * 50)
    
    # Import components
    try:
        from censor_utils import find_profane_segments, initialize_profanity_filter
        from whisper_transcribe import get_word_timestamps, get_segment_timestamps
        
        print("✅ All components loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing components: {e}")
        return
    
    # Initialize profanity filter
    print("\n🔧 Initializing profanity filter...")
    initialize_profanity_filter()
    
    # Create demo transcript
    print("📝 Creating demo transcript...")
    transcript_data = create_demo_transcript()
    
    print(f"\n📜 Original transcript:")
    print(f"'{transcript_data['text']}'")
    
    # Extract timestamps
    print("\n⏱️  Segment timestamps:")
    segments = get_segment_timestamps(transcript_data)
    for i, segment in enumerate(segments, 1):
        print(f"  {i}. [{segment['start']:.1f}s-{segment['end']:.1f}s]: '{segment['text']}'")
    
    print("\n🔍 Word-level timestamps:")
    words = get_word_timestamps(transcript_data)
    for word in words[:10]:  # Show first 10 words
        print(f"  '{word['word']}' at {word['start']:.1f}s-{word['end']:.1f}s")
    if len(words) > 10:
        print(f"  ... and {len(words) - 10} more words")
    
    # Detect profanity
    print("\n🚫 Detecting profane segments...")
    profane_segments = find_profane_segments(transcript_data)
    
    if profane_segments:
        print(f"Found {len(profane_segments)} profane segments:")
        for i, segment in enumerate(profane_segments, 1):
            print(f"  {i}. [{segment['start']:.1f}s-{segment['end']:.1f}s]: '{segment['text']}'")
            print(f"     Profane words: {segment['profane_words']}")
            print(f"     Type: {segment['type']}")
    else:
        print("No profane words detected.")
    
    print("\n🎉 Demo completed!")
    print("\n💡 In a real scenario:")
    print("   1. Audio would be extracted from video")
    print("   2. Whisper would transcribe the audio")
    print("   3. These segments would be replaced with beeps")
    print("   4. The cleaned audio would be merged back to video")
    
    print(f"\n📁 To process a real video, run:")
    print(f"   python main.py your_video.mp4")


if __name__ == "__main__":
    main()
