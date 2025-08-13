#!/usr/bin/env python3
"""
Render-specific startup script that ensures immediate port binding
"""
import os
import sys
import logging

# Set up logging immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the application with immediate port binding"""
    
    # Get PORT from environment (Render sets this)
    port = os.environ.get('PORT')
    if not port:
        logger.error("❌ PORT environment variable not set")
        sys.exit(1)
    
    try:
        port = int(port)
    except ValueError:
        logger.error(f"❌ Invalid PORT value: {port}")
        sys.exit(1)
    
    logger.info(f"🚀 Starting Censorly Backend for Render")
    logger.info(f"📍 Port: {port}")
    logger.info(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Import and test the app
    try:
        from app_supabase import app
        logger.info("✅ App imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import app: {e}")
        sys.exit(1)
    
    # Start the app immediately
    logger.info(f"🎯 Starting Flask server on 0.0.0.0:{port}")
    
    try:
        # Use Flask's built-in server for immediate startup
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False,
            use_debugger=False
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
