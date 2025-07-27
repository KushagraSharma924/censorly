#!/usr/bin/env python3
"""
Setup checker for ai-profanity-filter
Verifies that all dependencies and system requirements are met.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extract version info
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg is installed: {version_line}")
            return True
        else:
            print("❌ FFmpeg is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is NOT installed")
        print("   Install with: brew install ffmpeg (macOS)")
        print("                sudo apt install ffmpeg (Ubuntu)")
        print("                Download from https://ffmpeg.org/ (Windows)")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg check timed out")
        return False

def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage(Path.cwd())
        free_gb = free // (1024**3)
        print(f"💾 Available disk space: {free_gb} GB")
        
        if free_gb < 1:
            print("⚠️  Warning: Less than 1GB free space")
            print("   Video processing requires temporary storage")
            return False
        else:
            print("✅ Sufficient disk space available")
            return True
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
        return True

def main():
    """Run all setup checks."""
    print("🔍 ai-profanity-filter Setup Checker")
    print("=" * 40)
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
    print()
    
    # Check Python packages
    packages = [
        ("openai-whisper", "whisper"),
        ("ffmpeg-python", "ffmpeg"),
        ("better-profanity", "better_profanity"),
        ("pydub", "pydub"),
        ("numpy", "numpy")
    ]
    
    print("📦 Checking Python packages:")
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_good = False
    print()
    
    # Check ffmpeg
    if not check_ffmpeg():
        all_good = False
    print()
    
    # Check disk space
    if not check_disk_space():
        print("⚠️  Warning: Low disk space may cause issues")
    print()
    
    # Check project files
    required_files = [
        "main.py",
        "audio_utils.py", 
        "whisper_transcribe.py",
        "censor_utils.py",
        "requirements.txt"
    ]
    
    print("📁 Checking project files:")
    for filename in required_files:
        if Path(filename).exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} is missing")
            all_good = False
    print()
    
    # Final result
    if all_good:
        print("🎉 All checks passed! ai-profanity-filter is ready to use.")
        print("\n📋 Next steps:")
        print("   1. python test_components.py  # Test components")
        print("   2. python demo.py             # See demo")
        print("   3. python main.py video.mp4   # Process a video")
    else:
        print("❌ Some issues need to be resolved before using ai-profanity-filter.")
        print("\n🔧 To fix missing packages, run:")
        print("   pip install -r requirements.txt")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
