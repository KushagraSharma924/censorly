"""
Main application entry point for AI Profanity Filter.
Initializes the Flask application with the new modular structure.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from models.config_models import AppConfig
from api.app import create_app
from utils.config import setup_directories, setup_logging


def main():
    """Main application entry point."""
    
    # Load configuration
    config = AppConfig.from_env()
    
    # Setup directories
    setup_directories(config)
    
    # Setup logging
    setup_logging(config.logs_dir)
    
    # Create Flask app
    app = create_app(config)
    
    # Run the application
    print(f"🚀 Starting AI Profanity Filter on port {config.flask_port}")
    print(f"📁 Upload directory: {config.upload_dir}")
    print(f"📁 Processed directory: {config.processed_dir}")
    print(f"🤖 Whisper models: {config.whisper.default_model} (default), {config.whisper.hindi_model} (Hindi)")
    
    app.run(
        host='0.0.0.0',
        port=config.flask_port,
        debug=config.flask_debug
    )


if __name__ == "__main__":
    main()
