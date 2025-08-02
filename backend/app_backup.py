#!/usr/bin/env python3
"""
AI Profanity Filter SaaS Platform
Main Flask application for video processing and profanity filtering.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config import Config

import os
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import logging

# Import configuration
from config import Config

# Import models and database
from models.saas_models import db

# Import blueprints
from api.auth import auth_bp
from api.saas_routes import api_bp
from api.modern_routes import api_v2_bp

# Import Celery setup with fallback
try:
    from services.celery_worker import make_celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    def make_celery(app):
        return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    app.config['Config'] = Config  # For easy access
    
    # Debug database configuration
    logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize database migrations
    migrate = Migrate(app, db)
    
    # Configure CORS
    if config_name == 'development':
        CORS(app, 
             origins=[
                 "http://localhost:8080",
                 "http://localhost:5173", 
                 "http://127.0.0.1:3000",
                 "http://127.0.0.1:5173",
                 "http://localhost:5174",
                 "http://127.0.0.1:5174",
                 "http://127.0.0.1:8080"
             ],
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
        )
    else:
        # Production CORS
        cors_origins = app.config.get('CORS_ORIGINS', [])
        if cors_origins:
            CORS(app, 
                 origins=cors_origins,
                 supports_credentials=True,
                 allow_headers=['Content-Type', 'Authorization'],
                 methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
            )
        else:
            CORS(app, 
                 supports_credentials=True,
                 allow_headers=['Content-Type', 'Authorization'],
                 methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
            )
    
    # Initialize Celery if available
    if CELERY_AVAILABLE:
        celery = make_celery(app)
        app.celery = celery
    else:
        app.logger.warning("Celery not available - background processing disabled")
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(api_v2_bp)  # New v2 API with modern abuse classification
    
    # Create required directories
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    processed_folder = Path(app.config['PROCESSED_FOLDER'])
    wordlists_folder = Path('data/wordlists')
    
    upload_folder.mkdir(exist_ok=True)
    processed_folder.mkdir(exist_ok=True)
    wordlists_folder.mkdir(parents=True, exist_ok=True)
    
    # Create database tables
    with app.app_context():
        try:
            # Initialize Supabase connection
            from services.supabase_service import init_supabase_tables, setup_supabase_storage
            
            # Check Supabase connection
            supabase_initialized = init_supabase_tables()
            if supabase_initialized:
                app.logger.info("✅ Supabase connection established")
                setup_supabase_storage()
            else:
                app.logger.warning("⚠️ Supabase connection issues - check credentials")
            
            # Create SQLAlchemy tables
            db.create_all()
            app.logger.info("✅ Database tables created/verified")
            
        except Exception as e:
            app.logger.error(f"❌ Database initialization failed: {e}")
            # Continue anyway for development
        
        # Create default admin user if none exists
        from models.saas_models import User
        if not User.query.first():
            admin_user = User(
                email='admin@example.com',
                full_name='Admin User',
                subscription_tier='enterprise'
            )
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Created default admin user: admin@example.com")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check."""
        return {
            'status': 'healthy',
            'message': 'AI Profanity Filter SaaS Platform is running',
            'version': '2.0.0',
            'environment': config_name
        }
    
    # API documentation endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return {
            'message': 'AI Profanity Filter SaaS API',
            'version': '2.0.0',
            'endpoints': {
                'authentication': '/api/auth/*',
                'video_processing': '/api/upload, /api/jobs, /api/download',
                'training': '/api/train, /api/training',
                'user_data': '/api/stats, /api/dashboard',
                'utilities': '/api/plans, /api/formats'
            },
            'documentation': 'See README-SAAS.md for full API documentation'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return {'error': 'File too large'}, 413
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authentication required'}, 401
    
    return app


def main():
    """Main function to run the Flask application."""
    try:
        app = create_app()
        
        # Get port from environment or default to 9001
        port = int(os.environ.get('PORT', 9001))
        
        logger.info("🚀 Starting AI Profanity Filter SaaS Platform...")
        logger.info(f"📡 Server will run on port {port}")
        logger.info(f"🔐 JWT authentication enabled")
        logger.info(f"⚡ Background processing with Celery")
        logger.info(f"👥 Multi-user support enabled")
        logger.info("✅ SaaS Platform ready!")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=os.environ.get('FLASK_ENV') == 'development'
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
