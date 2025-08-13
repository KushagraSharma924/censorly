#!/bin/bash

# Deployment verification script for Render
echo "🚀 Censorly Backend Deployment Verification"
echo "============================================="

# Check Python version
echo "📍 Python version: $(python --version)"

# Check environment variables
echo "📍 PORT: ${PORT:-'Not set (will default to 10000)'}"
echo "📍 FLASK_ENV: ${FLASK_ENV:-'Not set (will default to production)'}"
echo "📍 Working directory: $(pwd)"

# Check if required files exist
echo ""
echo "📁 Checking required files..."
required_files=("app_supabase.py" "requirements.txt" ".env")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Test app import
echo ""
echo "🧪 Testing app import..."
python -c "
try:
    from app_supabase import app
    print('✅ App import successful')
    
    # Test health endpoint
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print('✅ Health endpoint working')
        else:
            print(f'❌ Health endpoint failed: {response.status_code}')
            
except Exception as e:
    print(f'❌ App import failed: {e}')
    exit(1)
"

echo ""
echo "🎯 Ready to start server on port ${PORT:-10000}"
echo "💡 Use: ./start.sh to start the server"
