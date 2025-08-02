#!/usr/bin/env python3
"""
Simple startup script for AI Profanity Filter.
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path so we can import from backend
current_dir = Path(__file__).parent.absolute()
backend_dir = current_dir.parent  # Go up one level from scripts to backend
sys.path.insert(0, str(backend_dir))

def main():
    """Start the Flask application."""
    try:
        print("🚀 Starting AI Profanity Filter...")
        
        # Import the app
        from app import create_app
        
        # Create app instance
        app = create_app()
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        
        print(f"✅ Server starting on http://0.0.0.0:{port}")
        print("📝 API Documentation:")
        print(f"   - Health check: http://localhost:{port}/api/v2/health")
        print(f"   - Test classifier: http://localhost:{port}/api/v2/test-classifier")
        print(f"   - Process video: http://localhost:{port}/api/v2/process-video")
        print("\n🎯 Ready for production!")
        
        # Start the server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('DEBUG', 'false').lower() == 'true'
        )
        
    except Exception as e:
        print(f"❌ Failed to start: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
