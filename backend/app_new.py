#!/usr/bin/env python3
"""
AI Profanity Filter - Refactored Flask Backend
Production-ready modular video processing API with support for multiple censoring modes.
"""

import os
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS
import logging

# Import our modular video processor
from video_processor import process_video, get_supported_modes, estimate_processing_time

# Import API routes
from api.routes import register_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS for multiple frontend ports
    CORS(app, origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ])
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
    
    # Create required directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    
    # Register API routes
    register_routes(app)
    
    return app


def main():
    """Main function to run the Flask application."""
    try:
        app = create_app()
        
        # Get port from environment or default to 9001
        port = int(os.environ.get('PORT', 9001))
        
        logger.info("🚀 Starting AI Profanity Filter Backend...")
        logger.info(f"📡 Server will run on port {port}")
        logger.info(f"🎬 Supported modes: {get_supported_modes()}")
        logger.info("✅ Backend ready for video processing!")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('FLASK_ENV') == 'development'
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
