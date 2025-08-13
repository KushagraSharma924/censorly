#!/bin/sh
# Production startup script for Censorly Backend API with error handling

set -e  # Exit on any error

# Print environment info for debugging
echo "=== Starting Censorly Backend API (Production) ==="
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Environment: ${FLASK_ENV:-production}"
echo "Port: ${PORT:-10000}"
echo "======================================================="

# Install production requirements
echo "Installing production requirements..."
pip install --no-cache-dir -r requirements-phase1.txt

# Test imports before starting the server
echo "Testing critical imports..."
python -c "
try:
    import flask
    print('✅ Flask imported successfully')
    import supabase
    print('✅ Supabase imported successfully') 
    from flask_session import Session
    print('✅ Flask-Session imported successfully')
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Unexpected error: {e}')
    exit(1)
"

# Test app creation
echo "Testing app creation..."
python -c "
try:
    from app_supabase import app
    print('✅ App created successfully')
except Exception as e:
    print(f'❌ App creation failed: {e}')
    exit(1)
"

# Set FLASK_APP for production mode
export FLASK_APP=app_supabase.py

# Start the main Supabase application
echo "Starting Supabase-based application..."
echo "PORT: ${PORT:-10000}"
echo "HOST: 0.0.0.0"
echo "Binding to: 0.0.0.0:${PORT:-10000}"

# Ensure PORT is set
if [ -z "$PORT" ]; then
    export PORT=10000
    echo "PORT not set, defaulting to 10000"
fi

# Start gunicorn directly with app_supabase:app
echo "Starting gunicorn with app_supabase:app on 0.0.0.0:$PORT"
exec gunicorn app_supabase:app \
  --bind "0.0.0.0:$PORT" \
  --workers=1 \
  --threads=4 \
  --timeout=120 \
  --keep-alive=2 \
  --log-level=info \
  --access-logfile=- \
  --error-logfile=- \
  --capture-output
