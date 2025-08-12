"""
Simplified Flask app for Render deployment debugging
This version has minimal dependencies and will start up quickly
"""

from flask import Flask, jsonify, render_template_string
import os
import platform
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Simple HTML template for root path
ROOT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Censorly API - Health Check</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        h1 { color: #4a5568; }
        .status { 
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 500;
            display: inline-block;
        }
        .status.ok { background-color: #c6f6d5; color: #22543d; }
        .banner {
            background: linear-gradient(90deg, #2d3748 0%, #4a5568 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
    </style>
</head>
<body>
    <div class="banner">
        <h1>Censorly API</h1>
        <p>Lightweight debug version</p>
    </div>
    
    <div class="card">
        <h2>Status: <span class="status ok">Running</span></h2>
        <p>Server Time: {{ server_time }}</p>
        <p>Startup Time: {{ startup_time }}</p>
    </div>
    
    <div class="card">
        <h2>System Information</h2>
        <div class="info-grid">
            <div>
                <strong>Python Version:</strong>
                <p>{{ python_version }}</p>
            </div>
            <div>
                <strong>Platform:</strong>
                <p>{{ system_platform }}</p>
            </div>
            <div>
                <strong>Environment:</strong>
                <p>{{ environment }}</p>
            </div>
            <div>
                <strong>Port:</strong>
                <p>{{ port }}</p>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>Next Steps</h2>
        <p>The lightweight API server is running. Check the logs for details on any issues with the main application.</p>
    </div>
</body>
</html>
"""

startup_time = datetime.utcnow().isoformat()

@app.route('/')
def root():
    """Root path with HTML status page"""
    context = {
        'server_time': datetime.utcnow().isoformat(),
        'startup_time': startup_time,
        'python_version': platform.python_version(),
        'system_platform': f"{platform.system()} {platform.release()}",
        'environment': os.getenv('FLASK_ENV', 'production'),
        'port': os.getenv('PORT', '10000')
    }
    return render_template_string(ROOT_TEMPLATE, **context)

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'ok',
        'message': 'Simplified API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'system_info': {
            'python_version': platform.python_version(),
            'platform': platform.system(),
            'release': platform.release()
        },
        'note': 'This is a lightweight version for debugging Render deployment issues'
    })

@app.route('/debug')
def debug():
    """Debug endpoint to check environment variables"""
    # Only return safe environment variables
    safe_env = {}
    for key in os.environ:
        if not any(secret in key.lower() for secret in ['secret', 'password', 'token', 'key']):
            safe_env[key] = os.environ[key]
    
    return jsonify({
        'environment': os.getenv('FLASK_ENV', 'production'),
        'safe_env_vars': safe_env,
        'sys_path': sys.path
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting lightweight debug server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
