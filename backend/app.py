"""
Enhanced SaaS Flask Application for AI Profanity Filter Platform
Complete production-ready Flask app with JWT auth, billing, and API management.
"""

from flask import Flask, jsonify, request, make_response, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_migrate import Migrate
from datetime import timedelta
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Import database models
from models.saas_models import db, User, Job, APIKey, Subscription, TrainingSession
from services.supabase_service import supabase_service

# Import route blueprints (with fallbacks for missing routes)
try:
    from api.auth_enhanced import auth_bp
except ImportError:
    print("Warning: auth_enhanced blueprint not available")
    auth_bp = None

try:
    from api.saas_routes_enhanced import saas_bp
except ImportError:
    print("Warning: saas_routes_enhanced blueprint not available")
    saas_bp = None

try:
    from api.modern_routes import api_v2_bp as modern_bp
except ImportError:
    modern_bp = None

# Skip legacy routes module as it has missing dependencies
routes_module = None

try:
    from api.payment_routes import payment_bp
except ImportError:
    print("Warning: payment_routes blueprint not available")
    payment_bp = None

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
     
    # Database configuration for Supabase PostgreSQL
    database_url = os.getenv('SUPABASE_DB_URL')
    if database_url and database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
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
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # CORS configuration - Enhanced for better frontend compatibility
    CORS(app, 
         origins=[
             "http://localhost:3000", 
             "http://localhost:5173", 
             "http://localhost:8080",
             "http://127.0.0.1:3000",
             "http://127.0.0.1:5173",
             "http://127.0.0.1:8080",
             "https://profanityfilter.ai"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=[
             "Content-Type", 
             "Authorization", 
             "X-API-Key",
             "X-Requested-With",
             "Accept",
             "Origin",
             "Access-Control-Request-Method",
             "Access-Control-Request-Headers"
         ],
         supports_credentials=True,
         expose_headers=["Content-Range", "X-Content-Range"],
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
        return jsonify({'error': 'Token is required'}), 401
    
    # Let Flask-CORS handle all CORS headers automatically
    
    # Register blueprints (only if available)
    if auth_bp:
        app.register_blueprint(auth_bp)  # Enhanced auth routes
    if saas_bp:
        app.register_blueprint(saas_bp)  # SaaS features (API keys, billing, usage)
    if payment_bp:
        app.register_blueprint(payment_bp)  # Payment and subscription routes
    if modern_bp:
        app.register_blueprint(modern_bp)  # Modern video processing routes
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            # Test database connection - check if we can query the users table
            from models.saas_models import User
            User.query.first()
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'service': 'AI Profanity Filter SaaS',
            'version': '2.0.0',
            'database': db_status,
            'features': [
                'jwt_authentication',
                'api_key_management',
                'subscription_billing',
                'multi_language_detection',
                'video_processing',
                'nsfw_content_detection',
                'real_time_processing'
            ]
        })

    # CORS test endpoint
    @app.route('/api/cors-test', methods=['GET', 'POST', 'OPTIONS'])
    def cors_test():
        """Test endpoint to verify CORS configuration."""
        return jsonify({
            'message': 'CORS is working correctly',
            'method': request.method,
            'origin': request.headers.get('Origin'),
            'cors_enabled': True
        })

    # Debug endpoint to test authentication
    @app.route('/api/debug/auth', methods=['GET'])
    @jwt_required()
    def debug_auth():
        """Debug endpoint to test JWT authentication."""
        try:
            user_id = get_jwt_identity()
            jwt_data = get_jwt()
            
            return jsonify({
                'authenticated': True,
                'user_id': user_id,
                'jwt_claims': jwt_data,
                'message': 'Authentication successful'
            })
        except Exception as e:
            return jsonify({
                'authenticated': False,
                'error': str(e)
            }), 500

    # Legacy route alias for backward compatibility
    @app.route('/api/process-video', methods=['POST', 'OPTIONS'])
    def process_video_legacy():
        """Legacy route that forwards to the v2 endpoint."""
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = make_response()
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        # For POST requests, forward to the actual handler
        try:
            from api.modern_routes import upload_and_process_video
            return upload_and_process_video()
        except ImportError:
            return jsonify({'error': 'Video processing service unavailable'}), 503

    # Legacy route alias for jobs endpoint
    @app.route('/api/jobs', methods=['GET', 'POST', 'OPTIONS'])
    def jobs_legacy():
        """Legacy route that returns empty jobs list for now."""
        if request.method == 'OPTIONS':
            return '', 200
        try:
            if request.method == 'GET':
                # Return empty jobs list for now
                return jsonify({'jobs': []}), 200
            else:
                return jsonify({'error': 'Method not implemented'}), 501
        except Exception as e:
            app.logger.error(f"Jobs endpoint error: {str(e)}")
            return jsonify({'error': 'Jobs service unavailable'}), 503    # Legacy route alias for individual job endpoint
    @app.route('/api/jobs/<job_id>', methods=['GET', 'OPTIONS'])
    def job_detail_legacy(job_id):
        """Legacy route that forwards to the v2 job detail endpoint."""
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        try:
            from api.modern_routes import get_job_status
            return get_job_status(job_id)  # Don't convert to int, keep as string UUID
        except ImportError:
            return jsonify({'error': 'Job service unavailable'}), 503
    
    # Download endpoint for processed videos
    @app.route('/api/download/<job_id>', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def download_processed_video(job_id):
        """Download processed video file."""
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        try:
            from api.modern_routes import get_current_user
            user = get_current_user()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Find the job
            from models.saas_models import Job
            job = Job.query.filter_by(id=job_id, user_id=user.id).first()
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            
            if job.status != 'completed' or not job.output_path:
                return jsonify({'error': 'Processed file not available'}), 404
            
            if not os.path.exists(job.output_path):
                return jsonify({'error': 'Output file not found on server'}), 404
            
            return send_file(
                job.output_path,
                as_attachment=True,
                download_name=f"processed_{job.original_filename}"
            )
            
        except Exception as e:
            return jsonify({'error': f'Download failed: {str(e)}'}), 500    # API documentation endpoint
    @app.route('/api/docs')
    def api_documentation():
        """API documentation and feature overview."""
        return jsonify({
            'service': 'AI Profanity Filter SaaS Platform',
            'version': '2.0.0',
            'description': 'Advanced profanity detection and content moderation API',
            'authentication': {
                'jwt': {
                    'endpoints': ['/api/auth/register', '/api/auth/login', '/api/auth/refresh'],
                    'description': 'JWT-based authentication for web dashboard'
                },
                'api_key': {
                    'header': 'X-API-Key',
                    'description': 'API key authentication for programmatic access'
                }
            },
            'endpoints': {
                'authentication': {
                    'POST /api/auth/register': 'Register new user',
                    'POST /api/auth/login': 'User login',
                    'POST /api/auth/refresh': 'Refresh access token',
                    'GET /api/auth/profile': 'Get user profile',
                    'PUT /api/auth/profile': 'Update user profile'
                },
                'api_management': {
                    'GET /api/keys': 'List API keys',
                    'POST /api/keys': 'Create new API key',
                    'DELETE /api/keys/<id>': 'Delete API key'
                },
                'subscription': {
                    'GET /api/plans': 'Get available plans',
                    'GET /api/subscription': 'Get current subscription',
                    'POST /api/subscription/upgrade': 'Upgrade subscription',
                    'GET /api/usage': 'Get usage statistics'
                },
                'video_processing': {
                    'POST /api/process': 'Process video (API key required)',
                    'POST /api/upload': 'Upload and process video (JWT required)',
                    'GET /api/jobs/<id>': 'Get job status',
                    'GET /api/jobs': 'List user jobs'
                },
                'webhooks': {
                    'POST /api/webhook/razorpay': 'Razorpay payment webhook'
                }
            },
            'supported_languages': ['english', 'hindi', 'hinglish', 'urdu'],
            'features': [
                'Real-time profanity detection',
                'Multi-language support',
                'Custom wordlist training',
                'Video censoring (beep/mute/cut)',
                'Subscription billing',
                'API rate limiting',
                'Usage analytics',
                'Background processing'
            ],
            'limits': {
                'free': {
                    'monthly_videos': 10,
                    'max_file_size': '100MB',
                    'max_duration': '5 minutes',
                    'whisper_model': 'base'
                },
                'basic': {
                    'monthly_videos': 100,
                    'max_file_size': '500MB',
                    'max_duration': '30 minutes',
                    'whisper_model': 'medium',
                    'price': '₹999/month'
                },
                'pro': {
                    'monthly_videos': 500,
                    'max_file_size': '1GB',
                    'max_duration': '60 minutes',
                    'whisper_model': 'large',
                    'price': '₹2999/month'
                },
                'enterprise': {
                    'monthly_videos': 'unlimited',
                    'max_file_size': '5GB',
                    'max_duration': '180 minutes',
                    'whisper_model': 'large',
                    'price': '₹9999/month'
                }
            }
        })
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        """Log incoming requests for debugging."""
        if request.endpoint and not request.endpoint.startswith('static'):
            app.logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    # Test endpoint for hybrid detector
    @app.route('/api/test-text', methods=['POST'])
    def test_text_detection():
        """Test endpoint for hybrid detector - no auth required for testing."""
        try:
            from services.hybrid_detector import HybridAbuseDetector
            
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Missing text field'}), 400
            
            text = data['text']
            detector = HybridAbuseDetector()
            result = detector.predict(text)
            
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"Test endpoint error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Database initialization - moved to app context
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Failed to create database tables: {str(e)}")
    
    return app

# Create the Flask app
app = create_app()

# Configure logging
if not app.debug:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    app.logger.setLevel(logging.INFO)
    app.logger.info('AI Profanity Filter SaaS Platform startup')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    print(f"""
🚀 AI Profanity Filter SaaS Platform
📍 Server: http://localhost:{port}
📚 API Docs: http://localhost:{port}/api/docs
🔍 Health: http://localhost:{port}/health
🌍 Environment: {'Development' if debug_mode else 'Production'}
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
