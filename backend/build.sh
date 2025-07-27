#!/usr/bin/env bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up directories..."
mkdir -p uploads outputs temp processed

echo "Backend build complete!"
