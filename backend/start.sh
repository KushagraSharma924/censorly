#!/bin/sh
# Production startup script for Censorly Backend API

# Print environment info for debugging
echo "Starting Censorly Backend API (Production)"
echo "Running with Python $(python --version)"
echo "Environment: $FLASK_ENV"
echo "Port: $PORT"

# Set FLASK_APP for production mode
export FLASK_APP=app_supabase.py

# Install production requirements
echo "Installing production requirements..."
pip install --no-cache-dir -r requirements-phase1.txt

# Start the main Supabase application
echo "Starting Supabase-based application..."
gunicorn app_supabase:app --bind 0.0.0.0:$PORT \
  --workers=1 \
  --threads=2 \
  --timeout=30 \
  --log-level=debug \
  --capture-output \
  --error-logfile=- \
  --access-logfile=-
