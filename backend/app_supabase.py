"""
Supabase-based Flask Application for AI Profanity Filter SaaS Platform
Complete production-ready Flask app using pure Supabase (no SQLAlchemy).
"""

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta, datetime
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Supabase service
from services.supabase_service import supabase_service

# Import route blueprints
try:
    from api.supabase_routes import supabase_bp
except ImportError:
    print("Warning: supabase_routes blueprint not available")
    supabase_bp = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application with Supabase."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads/')
    app.config['PROCESSED_FOLDER'] = os.getenv('PROCESSED_FOLDER', 'processed/')
    
    # Celery configuration
    app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Payment configuration
    app.config['RAZORPAY_KEY_ID'] = os.getenv('RAZORPAY_KEY_ID')
    app.config['RAZORPAY_KEY_SECRET'] = os.getenv('RAZORPAY_KEY_SECRET')
    app.config['RAZORPAY_WEBHOOK_SECRET'] = os.getenv('RAZORPAY_WEBHOOK_SECRET')
    
    # Initialize extensions (no SQLAlchemy)
    jwt = JWTManager(app)
    
    # CORS configuration - Railway friendly
    cors_origins = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "https://profanityfilter.ai",
        "https://ai-profanity-filter.vercel.app"
    ]
    
    # Add Render domain if deployed
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    if render_url:
        cors_origins.append(render_url)
    
    CORS(app, 
         origins=cors_origins,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=[
             "Content-Type", 
             "Authorization", 
             "X-API-Key",
             "X-Requested-With",
             "Accept",
             "Origin"
         ],
         supports_credentials=True,
         max_age=86400  # Cache preflight for 24 hours
    )
    
    # JWT configuration
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization header required'}), 401
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        if request.endpoint != 'static':
            logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    # Register blueprints
    if supabase_bp:
        app.register_blueprint(supabase_bp)
        logger.info("Supabase routes blueprint registered")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            # Test Supabase connection
            result = supabase_service.client.table("users").select("id").limit(1).execute()
            
            return jsonify({
                'status': 'healthy',
                'service': 'AI Profanity Filter SaaS',
                'database': 'supabase_connected',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.0.0',
                'features': [
                    'supabase_native',
                    'real_time_updates',
                    'row_level_security',
                    'api_key_management', 
                    'subscription_billing',
                    'multi_language_detection',
                    'video_processing'
                ]
            }), 200
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({'error': 'File too large'}), 413
    
    # Initialize Supabase service
    try:
        # Test Supabase connection on startup
        test_result = supabase_service.client.table("users").select("id").limit(1).execute()
        logger.info("✅ Supabase service connected successfully")
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {str(e)}")
        # Don't fail startup - let the app run and show errors in health check
    
    logger.info("🚀 AI Profanity Filter SaaS Platform startup")
    logger.info(f"📍 Server: http://localhost:8080")
    logger.info(f"📚 API Docs: http://localhost:8080/api/docs")
    logger.info(f"🔍 Health: http://localhost:8080/health")
    logger.info(f"🌍 Environment: {os.getenv('FLASK_ENV', 'Production')}")
    
    return app

def create_celery_app(app=None):
    """Create Celery app with Flask context."""
    app = app or create_app()
    
    try:
        from celery import Celery
        
        celery = Celery(
            app.import_name,
            backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL']
        )
        celery.conf.update(app.config)
        
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
        return celery
        
    except ImportError:
        logger.warning("Celery not available - background tasks disabled")
        return None

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
