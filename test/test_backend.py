#!/usr/bin/env python3
"""
Test script to verify the Flask backend is working correctly
Tests the API endpoints and video processing functionality
"""

import requests
import json
import time
import os
from pathlib import Path

API_BASE_URL = 'http://localhost:9001'

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f'{API_BASE_URL}/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed - Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - Is it running on port 9001?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_modes_endpoint():
    """Test the supported modes endpoint"""
    print("\n🔍 Testing modes endpoint...")
    try:
        response = requests.get(f'{API_BASE_URL}/modes')
        if response.status_code == 200:
            data = response.json()
            modes = data.get('supported_modes', [])
            print(f"✅ Modes endpoint works - Found {len(modes)} modes:")
            for mode in modes:
                status = "Ready" if mode.get('ready', False) else "Coming Soon"
                print(f"   - {mode['mode']}: {status}")
            return True
        else:
            print(f"❌ Modes endpoint failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Modes endpoint error: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print("\n🔍 Testing CORS configuration...")
    try:
        # Test preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f'{API_BASE_URL}/process', headers=headers)
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_methods = response.headers.get('Access-Control-Allow-Methods')
        
        if cors_origin:
            print(f"✅ CORS configured - Origin: {cors_origin}")
            if cors_methods:
                print(f"   Allowed methods: {cors_methods}")
            return True
        else:
            print("❌ CORS not properly configured")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_video_upload_without_file():
    """Test video upload endpoint without file (should fail gracefully)"""
    print("\n🔍 Testing video upload endpoint (no file)...")
    try:
        response = requests.post(f'{API_BASE_URL}/process', data={'mode': 'beep'})
        
        if response.status_code == 400:
            data = response.json()
            if 'No video file provided' in data.get('error', ''):
                print("✅ Upload endpoint properly rejects requests without files")
                return True
        
        print(f"❌ Upload endpoint didn't handle missing file correctly - Status: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False

def create_test_video():
    """Create a simple test video file for testing"""
    print("\n🎬 Creating test video file...")
    try:
        # Create a simple test video using ffmpeg if available
        test_file = "test_video.mp4"
        
        import subprocess
        result = subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=1',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5',
            '-c:v', 'libx264', '-c:a', 'aac', '-t', '5', '-y', test_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(test_file):
            print(f"✅ Test video created: {test_file}")
            return test_file
        else:
            print("⚠️ Could not create test video with ffmpeg")
            return None
            
    except FileNotFoundError:
        print("⚠️ ffmpeg not found - cannot create test video")
        return None
    except Exception as e:
        print(f"❌ Test video creation error: {e}")
        return None

def test_actual_video_processing():
    """Test actual video processing if test video is available"""
    print("\n🔍 Testing actual video processing...")
    
    test_file = create_test_video()
    if not test_file:
        print("⚠️ Skipping video processing test - no test file available")
        return True
    
    try:
        with open(test_file, 'rb') as f:
            files = {'video': (test_file, f, 'video/mp4')}
            data = {'mode': 'beep'}
            
            print("   Uploading and processing test video...")
            response = requests.post(f'{API_BASE_URL}/process', files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                # Check if response is a video file
                content_type = response.headers.get('content-type', '')
                if 'video' in content_type:
                    print("✅ Video processing successful - received processed video")
                    
                    # Save the result for verification
                    with open('processed_test_video.mp4', 'wb') as output:
                        output.write(response.content)
                    print("   Processed video saved as 'processed_test_video.mp4'")
                    
                    return True
                else:
                    print(f"❌ Expected video response, got: {content_type}")
                    return False
            else:
                print(f"❌ Video processing failed - Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text[:200]}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Video processing timed out (>60s)")
        return False
    except Exception as e:
        print(f"❌ Video processing error: {e}")
        return False
    finally:
        # Cleanup test file
        if os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Run all tests"""
    print("🧪 AI Profanity Filter Backend Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Modes Endpoint", test_modes_endpoint),
        ("CORS Configuration", test_cors),
        ("Upload Endpoint (No File)", test_video_upload_without_file),
        ("Video Processing", test_actual_video_processing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready for frontend integration.")
        print("\n📝 Next steps:")
        print("1. Start the frontend: cd frontend && npm run dev")
        print("2. Open http://localhost:3000")
        print("3. Test the full upload and download flow")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
        print("Make sure the backend is running: python app.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
