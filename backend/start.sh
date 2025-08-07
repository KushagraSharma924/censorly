#!/bin/bash
# Phase 1 Railway Startup Script

echo "🚀 Starting AI Profanity Filter Phase 1 Backend"
echo "📍 Port: $PORT"
echo "🌍 Environment: $FLASK_ENV"

# Start the application with Gunicorn
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --worker-class sync \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app_supabase:app
