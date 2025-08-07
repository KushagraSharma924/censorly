#!/bin/bash
# Test script for Render deployment
# Replace YOUR_APP_URL with your actual Render URL

APP_URL="https://your-app-name.onrender.com"

echo "🧪 Testing Render Deployment..."
echo "📍 App URL: $APP_URL"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$APP_URL/health" | jq '.' || echo "Health check failed"
echo ""

# Test 2: Root endpoint
echo "2. Testing Root Endpoint..."
curl -s "$APP_URL/" | jq '.' || echo "Root endpoint failed"
echo ""

# Test 3: Registration
echo "3. Testing User Registration..."
curl -s -X POST "$APP_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }' | jq '.' || echo "Registration failed"
echo ""

# Test 4: Login
echo "4. Testing User Login..."
curl -s -X POST "$APP_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com", 
    "password": "test123"
  }' | jq '.' || echo "Login failed"
echo ""

echo "✅ Testing complete!"
echo "🌐 Your API is live at: $APP_URL"
