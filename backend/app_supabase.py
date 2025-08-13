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

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Supabase service with error handling
try:
    from services.supabase_service import supabase_service
    SUPABASE_AVAILABLE = True
    logger.info("✅ Successfully imported supabase_service")
except ImportError as e:
    logger.error(f"❌ Supabase service not available: {e}")
    supabase_service = None
    SUPABASE_AVAILABLE = False

# Import route blueprints
try:
    from api.supabase_routes import supabase_bp
    logger.info("✅ Successfully imported supabase_routes blueprint")
except ImportError as e:
    logger.error(f"❌ Failed to import supabase_routes blueprint: {e}")
    supabase_bp = None

# Import health check routes (always available, no dependencies)
try:
    from api.health import health_bp
    logger.info("✅ Successfully imported health blueprint")
except ImportError as e:
    logger.error(f"❌ Failed to import health blueprint: {e}")
    health_bp = None

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
    
    # Configure session for CSRF
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    
    # Initialize Flask-Session
    from flask_session import Session
    Session(app)
    
    # CORS configuration - More permissive for development and production
    cors_origins = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "https://profanityfilter.ai",
        "https://ai-profanity-filter.vercel.app",
        "https://censorly.vercel.app",
        "https://*.vercel.app"  # Allow all Vercel apps
    ]
    
    # Add Render domain if deployed
    render_url = os.getenv('RENDER_EXTERNAL_URL')
    if render_url:
        cors_origins.append(render_url)
        cors_origins.append(render_url.replace('http:', 'https:'))  # Both HTTP and HTTPS
    
    # CORS configuration - More permissive setup
    CORS(app, 
         origins=cors_origins,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
         allow_headers=[
             "Content-Type", 
             "Authorization", 
             "X-API-Key",
             "X-Requested-With",
             "X-CSRF-TOKEN",
             "X-XSRF-TOKEN",
             "Accept",
             "Origin",
             "Access-Control-Request-Method",
             "Access-Control-Request-Headers"
         ],
         supports_credentials=True,  # Required for cookies including CSRF
         send_wildcard=False,
         max_age=86400
    )
    
    # Handle preflight requests globally
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            # Create a response with appropriate CORS headers
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-API-Key,X-Requested-With,Accept,Origin")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
            response.headers.add('Access-Control-Max-Age', '86400')
            return response
    
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
    else:
        logger.error("Supabase blueprint not available - application cannot start properly")
        raise RuntimeError("Missing required dependencies - check requirements.txt")
    
    # Register health check blueprint (high priority for render deployment)
    if health_bp:
        app.register_blueprint(health_bp)
        logger.info("Health check blueprint registered")
    else:
        logger.error("Health check blueprint not available")
        raise RuntimeError("Missing health check blueprint")
        @app.route('/', methods=['GET'])
        def root():
            """Root endpoint."""
            return jsonify({
                'service': 'AI Profanity Filter SaaS Backend',
                'status': 'running',
                'version': '1.0.0',
                'endpoints': {
                    'health': '/health',
                    'auth': '/api/auth/*',
                    'profile': '/api/profile/*',
                    'video': '/api/video/*'
                }
            })
        
        # Health check endpoint fallback if health_bp not available
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            try:
                # Test Supabase connection if available
                if SUPABASE_AVAILABLE and supabase_service:
                    result = supabase_service.client.table("users").select("id").limit(1).execute()
                
                return jsonify({
                    'status': 'healthy',
                    'service': 'AI Profanity Filter SaaS',
                    'database': 'supabase_connected' if SUPABASE_AVAILABLE else 'disconnected',
                    'timestamp': datetime.utcnow().isoformat(),
                    'version': '2.0.0',
                    'features': [
                        'supabase_native' if SUPABASE_AVAILABLE else 'database_unavailable',
                        'api_endpoints',
                        'cors_enabled'
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
    if SUPABASE_AVAILABLE and supabase_service:
        try:
            # Test Supabase connection on startup
            test_result = supabase_service.client.table("users").select("id").limit(1).execute()
            logger.info("✅ Supabase service connected successfully")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {str(e)}")
            logger.warning("⚠️ Application may not function properly without database connection")
    else:
        logger.error("⚠️ Supabase service not available - application requires database connection")
        raise RuntimeError("Database connection required")
    
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
    # Render deployment configuration
    port = int(os.environ.get('PORT', 10000))
    host = '0.0.0.0'  # Always bind to all interfaces for Render
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Censorly Backend on {host}:{port}")
    logger.info(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"🔍 Health check: http://{host}:{port}/health")
    
    # For production/Render, use a more robust server configuration
    if os.environ.get('FLASK_ENV') != 'development':
        logger.info("🏭 Production mode: Using threaded Flask server")
        app.run(
            host=host, 
            port=port, 
            debug=False, 
            threaded=True, 
            use_reloader=False,
            use_debugger=False
        )
    else:
        logger.info("🔧 Development mode")
        app.run(host=host, port=port, debug=debug, threaded=True)
