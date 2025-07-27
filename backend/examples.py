#!/usr/bin/env python3
"""
Usage examples for ai-profanity-filter
Shows different ways to use the system and handle edge cases.
"""

import sys
from pathlib import Path

def print_usage_examples():
    """Print various usage examples."""
    print("🎬 ai-profanity-filter - Usage Examples")
    print("=" * 50)
    
    print("\n📝 Basic Usage:")
    print("python main.py my_video.mp4")
    print("   → Creates: outputs/censored_my_video.mp4")
    
    print("\n📝 Custom Output Name:")
    print("python main.py movie.mp4 --output clean_movie.mp4")
    print("   → Creates: outputs/clean_movie.mp4")
    
    print("\n📝 Custom Temp Directory:")
    print("python main.py video.mp4 --temp-dir processing")
    print("   → Uses 'processing' folder for temporary files")
    
    print("\n📝 Full Example:")
    print("python main.py ~/Downloads/funny_video.mp4 \\")
    print("              --output family_friendly.mp4 \\")
    print("              --temp-dir temp_processing")
    
    print("\n🔧 Supported Video Formats:")
    formats = ["MP4", "AVI", "MOV", "MKV", "WMV", "FLV", "WebM"]
    print("   " + ", ".join(formats))
    
    print("\n⚠️  Requirements:")
    print("   • ffmpeg must be installed on your system")
    print("   • Video file must exist and be readable")
    print("   • Sufficient disk space for processing")
    print("   • Audio track in the video (silent videos won't work)")
    
    print("\n🎯 Processing Steps:")
    steps = [
        "Extract audio from video → temp/video_audio.wav",
        "Transcribe with Whisper → get text + timestamps", 
        "Detect profanity → find offensive segments",
        "Censor audio → replace with beeps/silence",
        "Merge back to video → final censored video"
    ]
    for i, step in enumerate(steps, 1):
        print(f"   {i}. {step}")
    
    print("\n📊 Expected Performance:")
    print("   • 1-minute video: ~30-60 seconds processing")
    print("   • 10-minute video: ~3-8 minutes processing")
    print("   • Processing time depends on:")
    print("     - Video length")
    print("     - Audio quality")
    print("     - Whisper model size (base is default)")
    print("     - CPU/GPU performance")
    
    print("\n🚨 Troubleshooting:")
    issues = [
        ("'ffmpeg not found'", "Install ffmpeg: brew install ffmpeg (macOS)"),
        ("'No module named whisper'", "Run: pip install -r requirements.txt"),
        ("'Video file not found'", "Check file path, use absolute path if needed"),
        ("'Permission denied'", "Check file permissions and disk space"),
        ("'No audio track found'", "Video must contain audio to process")
    ]
    
    for issue, solution in issues:
        print(f"   Problem: {issue}")
        print(f"   Solution: {solution}")
        print()

def main():
    """Main function."""
    print_usage_examples()
    
    print("🧪 Want to test the system?")
    print("   python test_components.py  # Test individual components")
    print("   python demo.py             # See profanity detection demo")
    
    print("\n📚 For more information:")
    print("   • Check README.md for detailed documentation")
    print("   • Look at main.py for the full processing pipeline")
    print("   • Examine individual modules for specific functionality")

if __name__ == "__main__":
    main()
