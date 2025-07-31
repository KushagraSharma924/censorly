#!/bin/bash

# Startup script for AI Profanity Filter Full-Stack App
# Runs both frontend (port 3000) and backend (port 9001)

echo "🎬 Starting AI Profanity Filter Full-Stack Application"
echo "=" 

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    echo "   Make sure you're in the directory containing 'frontend/' and 'backend/' folders"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
echo "🔍 Checking ports..."
check_port 3000 || echo "   Frontend may conflict with existing service on port 3000"
check_port 9001 || echo "   Backend may conflict with existing service on port 9001"

# Start backend in the background
echo "🚀 Starting Flask Backend (port 9001)..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🚀 Starting React Frontend (port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Show status
echo ""
echo "✅ Services started!"
echo "🌐 Frontend: http://localhost:3000"
echo "⚙️  Backend:  http://localhost:9001"
echo ""
echo "📋 Process IDs:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "⚠️  To stop both services, press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📖 Logs will appear below..."
echo "=" 

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup INT TERM

# Wait for both processes
wait
