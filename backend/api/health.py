"""
Simple health check module for Render deployment
This will allow the application to start up faster for debugging
"""

from flask import Blueprint, jsonify, render_template
import os
import sys
import platform
import logging

# Create blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint that doesn't require database connection"""
    try:
        # System information (helpful for debugging)
        system_info = {
            "python_version": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
            "flask_env": os.getenv("FLASK_ENV", "production"),
            "port": os.getenv("PORT", "10000"),
        }
        
        # Don't include sensitive environment variables
        env_subset = {}
        for key in ["FLASK_APP", "FLASK_ENV", "PORT", "RENDER_SERVICE_ID"]:
            if key in os.environ:
                env_subset[key] = os.environ[key]
        
        health_data = {
            "status": "ok",
            "message": "API server is running",
            "system": system_info,
            "env": env_subset,
        }
        
        return jsonify(health_data)
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Health check encountered an error: {str(e)}",
        }), 500

@health_bp.route('/', methods=['GET'])
def index():
    """Root endpoint to confirm server is running"""
    try:
        return render_template('health.html')
    except:
        return jsonify({
            "status": "ok",
            "message": "Censorly API is running",
            "docs": "/api/docs"
        })
