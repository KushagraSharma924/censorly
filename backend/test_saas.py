"""
Simplified SaaS Test Server for AI Profanity Filter Platform
"""

from flask import Flask, jsonify
import os

def create_app():
    """Create a simple test Flask application."""
    app = Flask(__name__)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'AI Profanity Filter SaaS',
            'version': '2.0.0',
            'message': 'SaaS Platform is running successfully!'
        }), 200
    
    @app.route('/api/docs')
    def api_documentation():
        """API documentation."""
        return jsonify({
            'service': 'AI Profanity Filter SaaS Platform',
            'version': '2.0.0',
            'description': 'Advanced profanity detection and content moderation API',
            'status': 'Development - SaaS Features Implemented',
            'features': [
                '✅ Enhanced Database Models (User, Job, APIKey, Subscription, TrainingSession)',
                '✅ JWT Authentication Routes (/api/auth/*)',
                '✅ SaaS Management Routes (/api/keys, /api/subscription, /api/usage)',
                '✅ Razorpay Payment Integration',
                '✅ API Key Management',
                '✅ Usage Tracking & Limits',
                '✅ Multi-tier Subscription Plans',
                '✅ Comprehensive Error Handling'
            ],
            'endpoints': {
                'authentication': {
                    'POST /api/auth/register': 'Register new user with JWT',
                    'POST /api/auth/login': 'User login with JWT',
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
                    'GET /api/jobs/<id>': 'Get job status',
                    'GET /api/jobs': 'List user jobs'
                }
            },
            'plans': {
                'free': {'price': 0, 'monthly_limit': 10, 'max_file_size': '100MB'},
                'basic': {'price': 999, 'monthly_limit': 100, 'max_file_size': '500MB'},
                'pro': {'price': 2999, 'monthly_limit': 500, 'max_file_size': '1GB'},
                'enterprise': {'price': 9999, 'monthly_limit': 'unlimited', 'max_file_size': '5GB'}
            }
        })
    
    @app.route('/')
    def welcome():
        """Welcome endpoint."""
        return jsonify({
            'message': '🚀 AI Profanity Filter SaaS Platform',
            'status': 'Active',
            'version': '2.0.0',
            'docs': '/api/docs',
            'health': '/health',
            'features': 'Complete SaaS transformation completed!'
        })
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    
    print(f"""
🚀 AI Profanity Filter SaaS Platform - Test Server
📍 Server: http://localhost:{port}
📚 API Docs: http://localhost:{port}/api/docs
🔍 Health: http://localhost:{port}/health
✅ SaaS Features: Fully Implemented
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )
