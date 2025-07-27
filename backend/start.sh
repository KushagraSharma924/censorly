#!/usr/bin/env bash
# Local development start script

echo "🎬 Starting MovieCensorAI Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads outputs temp processed

# Set environment variables for development
export FLASK_ENV=development
export PORT=5001

# Start the server
echo "🚀 Starting server on http://localhost:5001"
python server.py
