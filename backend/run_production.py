#!/usr/bin/env python3
"""
Production-ready startup script for Render deployment using gunicorn
"""

import os
import sys
import subprocess
import logging

def main():
    """Start the Flask app with gunicorn for production"""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get port from environment
    port = os.environ.get('PORT', '10000')
    host = '0.0.0.0'
    
    logger.info(f"🚀 Starting Censorly Backend (Production) on {host}:{port}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Test app import first
    try:
        from app_supabase import app
        logger.info("✅ App imported successfully")
        
        # Quick health check
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                logger.info("✅ Health endpoint working")
            else:
                logger.warning(f"⚠️ Health endpoint returned {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Failed to import/test app: {e}")
        sys.exit(1)
    
    # Build gunicorn command
    cmd = [
        'gunicorn',
        '--bind', f'{host}:{port}',
        '--workers', '1',
        '--threads', '4',
        '--timeout', '120',
        '--keep-alive', '2',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--log-level', 'info',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--capture-output',
        '--enable-stdio-inheritance',
        'app_supabase:app'
    ]
    
    logger.info(f"🎯 Starting gunicorn: {' '.join(cmd)}")
    
    try:
        # Use subprocess to run gunicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Gunicorn failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("❌ Gunicorn not found. Falling back to Flask development server.")
        fallback_to_flask(app, host, port, logger)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

def fallback_to_flask(app, host, port, logger):
    """Fallback to Flask development server if gunicorn fails"""
    logger.warning("⚠️ Using Flask development server (not recommended for production)")
    try:
        app.run(
            host=host,
            port=int(port),
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"❌ Flask server also failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
