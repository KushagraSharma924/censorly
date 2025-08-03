"""
SaaS API routes for AI Profanity Filter Platform
Handles API key management, billing, usage tracking, and subscriptions.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.saas_models import db, User, APIKey, Subscription, Job
from services.supabase_service import supabase_service
import logging
from datetime import datetime, timedelta
import uuid
from functools import wraps
import os
import hmac
import hashlib

saas_bp = Blueprint('saas', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

def get_whisper_model_for_tier(subscription_tier):
    """
    Determine the appropriate Whisper model based on subscription tier.
    
    Args:
        subscription_tier (str): User's subscription tier
        
    Returns:
        str: Whisper model name ('base', 'medium', or 'large')
    """
    tier_to_model = {
        'free': 'base',
        'basic': 'medium', 
        'pro': 'large',
        'enterprise': 'large'
    }
    
    return tier_to_model.get(subscription_tier, 'base')

# Plan configurations
PLAN_CONFIGS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'monthly_limit': 10,
        'max_file_size_mb': 100,
        'features': ['basic_profanity_detection', 'hindi_english_support']
    },
    'basic': {
        'name': 'Basic',
        'price': 999,  # INR
        'monthly_limit': 100,
        'max_file_size_mb': 500,
        'features': ['basic_profanity_detection', 'multi_language_support', 'api_access']
    },
    'pro': {
        'name': 'Professional',
        'price': 2999,  # INR
        'monthly_limit': 500,
        'max_file_size_mb': 1000,
        'features': ['advanced_detection', 'multi_language_support', 'api_access', 'priority_processing', 'custom_wordlists']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 9999,  # INR
        'monthly_limit': -1,  # Unlimited
        'max_file_size_mb': 5000,
        'features': ['all_features', 'dedicated_support', 'custom_integration', 'white_label']
    }
}

def api_key_required(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        
        # Validate API key
        key_obj = APIKey.verify_key(api_key)
        if not key_obj:
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not key_obj.is_active:
            return jsonify({'error': 'API key is inactive'}), 401
        
        # Check user subscription
        user = key_obj.user
        if not user.is_active:
            return jsonify({'error': 'User account is inactive'}), 403
        
        # Update last used timestamp
        key_obj.last_used = datetime.utcnow()
        key_obj.usage_count += 1
        db.session.commit()
        
        # Add to request context
        request.current_user = user
        request.current_api_key = key_obj
        
        return f(*args, **kwargs)
    return decorated_function

@saas_bp.route('/keys', methods=['GET'])
@jwt_required()
def list_api_keys():
    """List user's API keys."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Debug logging
        logger.info(f"Listing API keys for user {user_id} ({user.email})")
        all_keys = APIKey.query.all()
        logger.info(f"Total API keys in database: {len(all_keys)}")
        for key in all_keys:
            logger.info(f"Key {key.id}: user_id={key.user_id}, name={key.name}")
        
        keys = APIKey.query.filter_by(user_id=user.id).all()
        logger.info(f"User's API keys: {len(keys)}")
        
        return jsonify({
            'api_keys': [key.to_dict() for key in keys]
        }), 200
        
    except Exception as e:
        logger.error(f"List API keys error: {str(e)}")
        return jsonify({'error': 'Failed to list API keys'}), 500

@saas_bp.route('/keys', methods=['POST'])
@jwt_required()
def create_api_key():
    """Create a new API key."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        name = data.get('name', 'Unnamed Key').strip()
        
        if not name:
            return jsonify({'error': 'Key name is required'}), 400
        
        # Check if user has reached API key limit
        current_keys = APIKey.query.filter_by(user_id=user.id, is_active=True).count()
        if current_keys >= 10:  # Limit to 10 active keys per user
            return jsonify({'error': 'Maximum API keys limit reached'}), 400
        
        # Create new API key
        api_key = APIKey(user_id=user.id, name=name)
        raw_key = api_key.get_raw_key()
        
        db.session.add(api_key)
        db.session.commit()
        
        logger.info(f"New API key created for user: {user.email}")
        
        return jsonify({
            'message': 'API key created successfully',
            'api_key': raw_key,
            'key_info': api_key.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create API key error: {str(e)}")
        return jsonify({'error': 'Failed to create API key'}), 500

@saas_bp.route('/keys/<key_id>', methods=['DELETE'])
@jwt_required()
def delete_api_key(key_id):
    """Delete an API key."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        api_key = APIKey.query.filter_by(id=key_id, user_id=user.id).first()
        if not api_key:
            return jsonify({'error': 'API key not found'}), 404
        
        api_key.is_active = False
        api_key.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"API key deactivated for user: {user.email}")
        
        return jsonify({'message': 'API key deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete API key error: {str(e)}")
        return jsonify({'error': 'Failed to delete API key'}), 500

@saas_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get available subscription plans."""
    try:
        return jsonify({
            'plans': PLAN_CONFIGS
        }), 200
        
    except Exception as e:
        logger.error(f"Get plans error: {str(e)}")
        return jsonify({'error': 'Failed to get plans'}), 500

@saas_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get current user's subscription."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription = user.get_active_subscription()
        
        # Get usage statistics
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_usage = Job.query.filter(
            Job.user_id == user.id,
            Job.created_at >= current_month,
            Job.status == 'completed'
        ).count()
        
        limits = user.get_plan_limits()
        
        return jsonify({
            'subscription': subscription.to_dict() if subscription else None,
            'usage': {
                'monthly_videos': monthly_usage,
                'monthly_limit': limits['monthly_limit'],
                'remaining': limits['monthly_limit'] - monthly_usage if limits['monthly_limit'] > 0 else -1
            },
            'limits': limits
        }), 200
        
    except Exception as e:
        logger.error(f"Get subscription error: {str(e)}")
        return jsonify({'error': 'Failed to get subscription'}), 500

@saas_bp.route('/subscription/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Upgrade user's subscription plan."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        plan_name = data.get('plan')
        
        if plan_name not in PLAN_CONFIGS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan_config = PLAN_CONFIGS[plan_name]
        
        # Create Razorpay order (placeholder for now)
        order_id = f"order_{uuid.uuid4().hex[:16]}"
        
        # Create pending subscription
        subscription = Subscription(
            user_id=user.id,
            plan_name=plan_name,
            plan_price=plan_config['price'],
            status='pending',
            razorpay_order_id=order_id
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription upgrade initiated',
            'order_id': order_id,
            'amount': plan_config['price'],
            'currency': 'INR',
            'plan': plan_config
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Upgrade subscription error: {str(e)}")
        return jsonify({'error': 'Failed to upgrade subscription'}), 500

@saas_bp.route('/usage', methods=['GET'])
@jwt_required()
def get_usage():
    """Get detailed usage statistics."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get usage for different time periods
        now = datetime.utcnow()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Monthly usage
        monthly_jobs = Job.query.filter(
            Job.user_id == user.id,
            Job.created_at >= current_month
        ).all()
        
        last_month_jobs = Job.query.filter(
            Job.user_id == user.id,
            Job.created_at >= last_month,
            Job.created_at < current_month
        ).all()
        
        # API key usage
        api_keys = APIKey.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            'current_month': {
                'total_jobs': len(monthly_jobs),
                'completed_jobs': len([j for j in monthly_jobs if j.status == 'completed']),
                'failed_jobs': len([j for j in monthly_jobs if j.status == 'failed']),
                'processing_time': sum(j.processing_time or 0 for j in monthly_jobs)
            },
            'last_month': {
                'total_jobs': len(last_month_jobs),
                'completed_jobs': len([j for j in last_month_jobs if j.status == 'completed']),
                'failed_jobs': len([j for j in last_month_jobs if j.status == 'failed']),
                'processing_time': sum(j.processing_time or 0 for j in last_month_jobs)
            },
            'api_keys': [
                {
                    'name': key.name,
                    'usage_count': key.usage_count,
                    'last_used': key.last_used.isoformat() if key.last_used else None
                }
                for key in api_keys if key.is_active
            ],
            'limits': user.get_plan_limits()
        }), 200
        
    except Exception as e:
        logger.error(f"Get usage error: {str(e)}")
        return jsonify({'error': 'Failed to get usage'}), 500

@saas_bp.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay payment webhooks."""
    try:
        # Verify webhook signature
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        if not webhook_secret:
            logger.error("Razorpay webhook secret not configured")
            return jsonify({'error': 'Webhook not configured'}), 500
        
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            return jsonify({'error': 'Missing signature'}), 400
        
        # Verify signature
        payload = request.get_data()
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Process webhook event
        event = request.get_json()
        event_type = event.get('event')
        
        if event_type == 'payment.captured':
            # Handle successful payment
            payment_data = event['payload']['payment']['entity']
            order_id = payment_data.get('order_id')
            
            # Find subscription by order ID
            subscription = Subscription.query.filter_by(razorpay_order_id=order_id).first()
            if subscription:
                subscription.status = 'active'
                subscription.razorpay_payment_id = payment_data.get('id')
                subscription.start_date = datetime.utcnow()
                subscription.end_date = datetime.utcnow() + timedelta(days=30)
                
                # Update user subscription tier
                user = subscription.user
                user.subscription_tier = subscription.plan_name
                
                db.session.commit()
                
                logger.info(f"Payment captured for subscription: {subscription.id}")
        
        elif event_type == 'payment.failed':
            # Handle failed payment
            payment_data = event['payload']['payment']['entity']
            order_id = payment_data.get('order_id')
            
            subscription = Subscription.query.filter_by(razorpay_order_id=order_id).first()
            if subscription:
                subscription.status = 'failed'
                db.session.commit()
                
                logger.info(f"Payment failed for subscription: {subscription.id}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

# API endpoint for programmatic access
@saas_bp.route('/process', methods=['POST'])
@api_key_required  
def api_process_video():
    """Process video via API with API key authentication."""
    try:
        user = request.current_user
        api_key = request.current_api_key
        
        # Check usage limits
        limits = user.get_plan_limits()
        if limits['monthly_limit'] > 0:
            current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_usage = Job.query.filter(
                Job.user_id == user.id,
                Job.created_at >= current_month,
                Job.status == 'completed'
            ).count()
            
            if monthly_usage >= limits['monthly_limit']:
                return jsonify({'error': 'Monthly limit exceeded'}), 429
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get processing parameters from form with defaults
        censoring_mode = request.form.get('censoring_mode', 'beep')
        abuse_threshold = float(request.form.get('abuse_threshold', 0.3))
        languages = request.form.get('languages', 'auto').split(',')
        
        # Determine Whisper model based on user's subscription tier
        whisper_model = get_whisper_model_for_tier(user.subscription_tier)
        
        # Use existing video processing logic from modern_routes
        # For now, return the configuration that would be used
        return jsonify({
            'message': 'Video processing initiated',
            'user_id': str(user.id),
            'api_key_name': api_key.name,
            'processing_config': {
                'censoring_mode': censoring_mode,
                'abuse_threshold': abuse_threshold,
                'languages': languages,
                'whisper_model': whisper_model,
                'subscription_tier': user.subscription_tier
            }
        }), 202
        
    except Exception as e:
        logger.error(f"API process video error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500
