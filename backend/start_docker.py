#!/usr/bin/env python3
"""
Docker-optimized startup script for Render deployment
Handles Docker networking and port binding correctly
"""
import os
import sys
import logging
import socket
import time

# Set up logging immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

def check_port_available(port):
    """Check if port is available for binding"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def wait_for_app_ready(port, max_wait=30):
    """Wait for the app to be ready on the specified port"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                if result == 0:
                    logger.info(f"✅ Port {port} is now accepting connections")
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    """Start the application with Docker-compatible networking"""
    
    logger.info("🐳 Starting Censorly Backend (Docker Mode)")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    
    # Get PORT from environment (Render sets this)
    port = os.environ.get('PORT')
    if not port:
        logger.error("❌ PORT environment variable not set by Render")
        sys.exit(1)
    
    try:
        port = int(port)
    except ValueError:
        logger.error(f"❌ Invalid PORT value: {port}")
        sys.exit(1)
    
    logger.info(f"📍 Target port: {port}")
    logger.info(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Check if port is available
    if not check_port_available(port):
        logger.error(f"❌ Port {port} is already in use")
        sys.exit(1)
    
    logger.info(f"✅ Port {port} is available")
    
    # Import and test the app
    try:
        logger.info("📦 Importing Flask application...")
        from app_supabase import app
        logger.info("✅ App imported successfully")
        
        # Quick health test
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                logger.info("✅ Health endpoint test passed")
            else:
                logger.warning(f"⚠️ Health endpoint returned {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Failed to import/test app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Start the app with Docker-compatible settings
    logger.info(f"🚀 Starting Flask server on 0.0.0.0:{port}")
    logger.info("🐳 Docker mode: Binding to all interfaces")
    
    try:
        # Use Flask's built-in server with Docker-friendly settings
        app.run(
            host='0.0.0.0',  # Essential for Docker containers
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False,
            use_debugger=False,
            load_dotenv=False  # We already loaded env vars
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
