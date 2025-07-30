#!/usr/bin/env python3
"""
Example usage script for the modular AI Profanity Filter
Demonstrates how to use the new modular architecture
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from video_processor import process_video, get_supported_modes, estimate_processing_time


def main():
    """Example usage of the modular video processor"""
    
    print("🎬 AI Profanity Filter - Modular Usage Example")
    print("=" * 50)
    
    # Show supported modes
    print("\n📋 Supported Processing Modes:")
    modes = get_supported_modes()
    for mode in modes:
        status = "✅ Ready" if mode.get('ready', False) else "🚧 Coming Soon"
        print(f"  - {mode['mode']}: {mode['description']} ({status})")
    
    # Example video file (replace with your actual video)
    video_path = "test_video.mp4"
    
    if not Path(video_path).exists():
        print(f"\n⚠️  Test video '{video_path}' not found.")
        print("Please place a test video file in the current directory and update the path.")
        return
    
    print(f"\n🎯 Processing video: {video_path}")
    
    # Example 1: Estimate processing time
    print("\n⏱️  Estimating processing time...")
    try:
        estimation = estimate_processing_time(video_path, 'beep')
        print(f"Video duration: {estimation['video_duration']:.2f} seconds")
        print(f"File size: {estimation['file_size_mb']:.2f} MB")
        print(f"Estimated processing time: {estimation['estimated_processing_time']:.2f} seconds")
    except Exception as e:
        print(f"❌ Estimation failed: {e}")
        return
    
    # Example 2: Process with beep mode
    print("\n🔊 Processing with BEEP mode...")
    try:
        result = process_video(
            input_path=video_path,
            mode='beep',
            custom_words=['example', 'test']  # Add custom words to filter
        )
        
        print("✅ Processing completed!")
        print(f"Job ID: {result['job_id']}")
        print(f"Segments processed: {result['segments_processed']}")
        print(f"Output file: {result['output_path']}")
        print(f"Steps completed: {', '.join(result['steps_completed'])}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
    
    # Example 3: Process with mute mode
    print("\n🔇 Processing with MUTE mode...")
    try:
        result = process_video(
            input_path=video_path,
            mode='mute'
        )
        
        print("✅ Processing completed!")
        print(f"Output file: {result['output_path']}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
    
    # Example 4: Try NSFW detection (will show placeholder)
    print("\n👁️  Testing NSFW detection (placeholder)...")
    try:
        result = process_video(
            input_path=video_path,
            mode='cut-nsfw',
            nsfw_model='nudenet'
        )
        
        print("✅ NSFW processing completed!")
        print(f"Output file: {result['output_path']}")
        
    except Exception as e:
        print(f"❌ NSFW processing failed: {e}")
    
    print("\n🎉 Example completed! Check the 'processed/' folder for output files.")


def example_direct_module_usage():
    """Example of using individual modules directly"""
    
    print("\n🔧 Direct Module Usage Examples")
    print("=" * 40)
    
    # Example: Using transcription module directly
    print("\n1. Direct transcription example:")
    print("```python")
    print("from modules.transcribe import transcribe_with_whisper")
    print("result = transcribe_with_whisper('audio.wav')")
    print("print(result['text'])")
    print("```")
    
    # Example: Using word detection directly
    print("\n2. Direct word detection example:")
    print("```python")
    print("from modules.detect_words import detect_abusive_words")
    print("segments = detect_abusive_words(transcript_data)")
    print("print(f'Found {len(segments)} profane segments')")
    print("```")
    
    # Example: Using FFmpeg tools directly
    print("\n3. Direct FFmpeg usage example:")
    print("```python")
    print("from modules.ffmpeg_tools import extract_audio, apply_beep")
    print("extract_audio('video.mp4', 'audio.wav')")
    print("apply_beep('audio.wav', segments, 'censored.wav')")
    print("```")
    
    # Example: Adding custom profanity words
    print("\n4. Custom profanity words example:")
    print("```python")
    print("from modules.detect_words import add_custom_profanity_words")
    print("add_custom_profanity_words(['custom_word1', 'custom_word2'])")
    print("```")


def show_future_ai_integration():
    """Show how future AI models will be integrated"""
    
    print("\n🚀 Future AI Model Integration")
    print("=" * 40)
    
    print("\n📝 To add NudeNet for NSFW detection:")
    print("1. Uncomment 'nudenet==2.0.9' in requirements.txt")
    print("2. Update modules/detect_nsfw.py with actual model loading:")
    print("```python")
    print("from nudenet import NudeDetector")
    print("detector = NudeDetector()")
    print("results = detector.detect('frame.jpg')")
    print("```")
    
    print("\n📝 To add custom CNN model:")
    print("1. Uncomment PyTorch/TensorFlow in requirements.txt")
    print("2. Update modules/detect_nsfw.py with your model:")
    print("```python")
    print("import torch")
    print("model = torch.load('your_model.pth')")
    print("prediction = model(processed_frame)")
    print("```")
    
    print("\n📝 The modular structure makes it easy to plug in new models!")


if __name__ == "__main__":
    # Run the main example
    main()
    
    # Show additional examples
    example_direct_module_usage()
    show_future_ai_integration()
