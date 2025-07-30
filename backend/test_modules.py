#!/usr/bin/env python3
"""
Test script for the modular AI Profanity Filter
Validates that all modules can be imported and basic functions work
"""

import sys
import traceback
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from modules.transcribe import transcribe_with_whisper, get_word_timestamps
        print("✅ transcribe.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import transcribe.py: {e}")
        return False
    
    try:
        from modules.detect_words import detect_abusive_words, add_custom_profanity_words
        print("✅ detect_words.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import detect_words.py: {e}")
        return False
    
    try:
        from modules.detect_nsfw import detect_nsfw_scenes
        print("✅ detect_nsfw.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import detect_nsfw.py: {e}")
        return False
    
    try:
        from modules.ffmpeg_tools import extract_audio, apply_beep, apply_mute
        print("✅ ffmpeg_tools.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ffmpeg_tools.py: {e}")
        return False
    
    try:
        from video_processor import process_video, get_supported_modes
        print("✅ video_processor.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import video_processor.py: {e}")
        return False
    
    try:
        import app
        print("✅ app.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import app.py: {e}")
        return False
    
    return True


def test_profanity_detection():
    """Test profanity detection functionality"""
    print("\n🧪 Testing profanity detection...")
    
    try:
        from modules.detect_words import detect_profane_words, test_profanity_detection
        
        # Test basic profanity detection
        test_text = "This is a damn test sentence"
        profane_words = detect_profane_words(test_text)
        print(f"✅ Profane words detected in test text: {profane_words}")
        
        # Test profanity detection function
        result = test_profanity_detection("This is a test")
        print(f"✅ Profanity test result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Profanity detection test failed: {e}")
        traceback.print_exc()
        return False


def test_supported_modes():
    """Test supported modes function"""
    print("\n🧪 Testing supported modes...")
    
    try:
        from video_processor import get_supported_modes
        
        modes = get_supported_modes()
        print(f"✅ Found {len(modes)} supported modes:")
        for mode in modes:
            status = "Ready" if mode.get('ready', False) else "Coming Soon"
            print(f"  - {mode['mode']}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supported modes test failed: {e}")
        traceback.print_exc()
        return False


def test_nsfw_placeholder():
    """Test NSFW detection placeholder"""
    print("\n🧪 Testing NSFW detection placeholder...")
    
    try:
        from modules.detect_nsfw import detect_nsfw_scenes
        
        # Test with non-existent file (should handle gracefully)
        result = detect_nsfw_scenes("fake_video.mp4", "nudenet")
        print(f"✅ NSFW detection placeholder returned: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ NSFW detection test failed: {e}")
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config, DevelopmentConfig, ProductionConfig
        
        print(f"✅ Base config loaded - Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"✅ Dev config loaded - Debug: {DevelopmentConfig.DEBUG}")
        print(f"✅ Prod config loaded - Debug: {ProductionConfig.DEBUG}")
        print(f"✅ Allowed extensions: {Config.ALLOWED_EXTENSIONS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False


def check_dependencies():
    """Check if required dependencies are available"""
    print("\n🧪 Checking dependencies...")
    
    dependencies = [
        ('flask', 'Flask web framework'),
        ('flask_cors', 'Flask CORS extension'),
        ('werkzeug', 'WSGI toolkit'),
        ('better_profanity', 'Profanity detection'),
        ('pydub', 'Audio processing'),
        ('ffmpeg', 'FFmpeg Python wrapper'),
    ]
    
    missing_deps = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: {description}")
        except ImportError:
            print(f"❌ {dep}: {description} - NOT FOUND")
            missing_deps.append(dep)
    
    # Check optional dependencies
    optional_deps = [
        ('whisper', 'OpenAI Whisper - Required for transcription'),
        ('cv2', 'OpenCV - Required for future NSFW detection'),
        ('numpy', 'NumPy - Required for future AI models'),
    ]
    
    print("\n📦 Optional dependencies (for full functionality):")
    for dep, description in optional_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}: {description}")
        except ImportError:
            print(f"⚠️  {dep}: {description} - NOT FOUND (optional)")
    
    if missing_deps:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🎬 AI Profanity Filter - Module Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", check_dependencies),
        ("Profanity Detection", test_profanity_detection),
        ("Supported Modes", test_supported_modes),
        ("NSFW Placeholder", test_nsfw_placeholder),
        ("Configuration", test_configuration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"🧪 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular system is ready to use.")
        print("\n📝 Next steps:")
        print("1. Place a test video file and run: python example_usage.py")
        print("2. Start the Flask server: python app.py")
        print("3. Add AI models by uncommenting dependencies in requirements.txt")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
