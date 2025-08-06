"""
Phase 1 Development Server - No Supabase Required
Simple Flask server for testing without Supabase configuration.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_dev_app():
    """Create a simple dev app without Supabase dependencies."""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    # Enable CORS for frontend
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "🚀 AI Profanity Filter - Phase 1 Development Server",
            "status": "running",
            "phase": "1",
            "features": [
                "Simple JWT Auth (via Supabase)",
                "Regex + Scikit-learn Detection", 
                "Video Processing (beep/mute modes)",
                "API Key Management",
                "Tiered Access (Free/Basic)"
            ],
            "setup_required": [
                "Configure Supabase credentials in backend/.env",
                "Update SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY"
            ]
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "phase": "1"})
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            "api_status": "available",
            "version": "1.0.0",
            "phase": "1",
            "supabase_configured": bool(os.getenv('SUPABASE_URL'))
        })
    
    return app

if __name__ == '__main__':
    app = create_dev_app()
    print("🚀 Starting Phase 1 Development Server...")
    print("📍 Available at: http://localhost:8080")
    print("🔧 Configure Supabase in .env for full functionality")
    app.run(debug=True, host='0.0.0.0', port=8080)
