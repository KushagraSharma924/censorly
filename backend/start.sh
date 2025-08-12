#!/bin/sh
# Simplified startup script for debugging Render deployment issues

# Print environment info for debugging
echo "Starting Censorly Backend API in Debug Mode"
echo "Running with Python $(python --version)"
echo "Environment: $FLASK_ENV"
echo "Port: $PORT"

# Set FLASK_APP for debug mode
export FLASK_APP=app_debug.py

# Install minimal requirements first (in case requirements-phase1.txt has issues)
echo "Installing minimal debug requirements..."
pip install --no-cache-dir -r requirements-debug.txt

# Try to determine why startup is timing out on Render
# First try the minimal debug app which has minimal dependencies
echo "Starting minimal debug app..."
gunicorn app_debug:app --bind 0.0.0.0:$PORT \
  --workers=1 \
  --threads=2 \
  --timeout=30 \
  --log-level=debug \
  --capture-output \
  --error-logfile=- \
  --access-logfile=-
