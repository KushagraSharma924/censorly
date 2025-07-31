#!/usr/bin/env bash
# Production deployment script

echo "🚀 Setting up AI Profanity Filter Backend..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads processed logs data/wordlists data/models

# Set permissions
chmod +x app.py

echo "✅ Backend setup complete!"
echo "🎯 Run with: python3 app.py"
