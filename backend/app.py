"""
Production Flask Application for Censorly - AI Profanity Filter SaaS Platform
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services and routes
from services.supabase_service import supabase_service
from api.supabase_routes import supabase_bp
from api.health import health_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure Flask
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Use same secret for JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Don't expire access tokens for now
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Configure CORS for production
    CORS(app, 
         origins=['https://censorly.vercel.app', 'http://localhost:3000'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(supabase_bp)
    
    @app.route('/')
    def home():
        return {
            'status': 'success',
            'message': 'Censorly API is running',
            'version': '1.0.0'
        }
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
