#!/bin/bash

# Production deployment script for Censorly backend
# This script ensures all dependencies are properly installed

echo "🚀 Censorly Backend Deployment Script"
echo "======================================"

# Check if we're in the backend directory
if [ ! -f "app_supabase.py" ]; then
    echo "❌ Error: Must run from backend directory"
    exit 1
fi

# Install system dependencies for python-magic
echo "📦 Installing system dependencies..."

# For Ubuntu/Debian systems (common on cloud platforms)
if command -v apt-get &> /dev/null; then
    echo "🐧 Detected Debian/Ubuntu system"
    sudo apt-get update
    sudo apt-get install -y libmagic1 libmagic-dev
fi

# For CentOS/RHEL systems
if command -v yum &> /dev/null; then
    echo "🎩 Detected CentOS/RHEL system"
    sudo yum install -y file-devel
fi

# For macOS (if running locally)
if command -v brew &> /dev/null; then
    echo "🍺 Detected macOS with Homebrew"
    brew install libmagic
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."

# Try to install from requirements.txt first
if [ -f "requirements.txt" ]; then
    echo "📋 Installing from requirements.txt..."
    pip install -r requirements.txt
elif [ -f "requirements-phase1.txt" ]; then
    echo "📋 Installing from requirements-phase1.txt..."
    pip install -r requirements-phase1.txt
else
    echo "❌ No requirements file found!"
    exit 1
fi

# Test the installation
echo "🧪 Testing installation..."
python3 test_dependencies.py

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌟 Ready to start with: python3 app_supabase.py"
else
    echo "❌ Deployment failed - check dependencies"
    exit 1
fi

echo ""
echo "🎯 Quick Start Commands:"
echo "  Development: python3 app_supabase.py"
echo "  Production:  gunicorn -w 4 -b 0.0.0.0:8080 app_supabase:app"
echo ""
