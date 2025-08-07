#!/bin/bash
# Phase 1 Render Startup Script

echo "🚀 Starting AI Profanity Filter Phase 1 Backend"
echo "📍 Port: $PORT"
echo "🌍 Environment: $FLASK_ENV"
echo "🔧 Platform: Render"

# Start the application with Gunicorn optimized for Render
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --worker-class sync \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    app_supabase:app
