#!/bin/bash
"""
Start SaaS Platform - Backend and Frontend
"""

# Load environment variables
export SUPABASE_DB_URL="postgresql://postgres:kushnbrc0924@db.sepwsbpbogvcccvonxdd.supabase.co:5432/postgres"
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "🚀 Starting AI Profanity Filter SaaS Platform"
echo "================================================"

# Start backend server
echo "📡 Starting Backend Server..."
cd /Users/kushagra/Desktop/ai-profanity-filter/backend

# Try to start the enhanced SaaS server first
if [ -f "app_saas.py" ]; then
    echo "✅ Starting Enhanced SaaS Server (app_saas.py)"
    python3 test_saas.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
else
    echo "✅ Starting Original Server (app.py)"
    python3 app.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
fi

sleep 3

# Check if backend started successfully
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Backend server is running on http://localhost:8080"
else
    echo "❌ Backend server failed to start"
fi

# Start frontend
echo ""
echo "🎨 Starting Frontend Server..."
cd /Users/kushagra/Desktop/ai-profanity-filter/frontend

if [ -f "package.json" ]; then
    echo "✅ Installing frontend dependencies..."
    bun install
    
    echo "✅ Starting frontend development server..."
    bun run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    sleep 5
    
    if curl -s http://localhost:5173 > /dev/null; then
        echo "✅ Frontend server is running on http://localhost:5173"
    else
        echo "❌ Frontend server failed to start"
    fi
else
    echo "❌ Frontend package.json not found"
fi

echo ""
echo "🎉 SaaS Platform Started!"
echo "📍 Backend:  http://localhost:8080"
echo "📍 Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8080/api/docs"
echo "🔍 Health:   http://localhost:8080/health"
echo ""
echo "Press Ctrl+C to stop both servers"

# Keep the script running
wait
