#!/usr/bin/env python3
"""
Direct Python startup script for Render deployment
This bypasses shell script issues and starts the server directly
"""

import os
import sys
import logging

def main():
    """Start the Flask app directly"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get port from environment
    port = int(os.environ.get('PORT', 10000))
    host = '0.0.0.0'
    
    logger.info(f"🚀 Starting Censorly Backend on {host}:{port}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Test app import first
    try:
        from app_supabase import app
        logger.info("✅ App imported successfully")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                logger.info("✅ Health endpoint working")
            else:
                logger.warning(f"⚠️ Health endpoint returned {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Failed to import/test app: {e}")
        sys.exit(1)
    
    # Start the Flask development server (Render compatible)
    logger.info(f"🎯 Starting Flask server on {host}:{port}")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
