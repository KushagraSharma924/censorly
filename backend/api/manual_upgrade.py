"""
Manual upgrade endpoints for testing payment system
"""

from flask import Blueprint, request, jsonify, g
from api.supabase_routes import supabase_auth_required
from services.supabase_service import supabase_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create manual upgrade blueprint
manual_bp = Blueprint('manual', __name__, url_prefix='/api/manual')

@manual_bp.route('/upgrade-user', methods=['POST'])
@supabase_auth_required
def manual_upgrade_user():
    """Manually upgrade a user for testing purposes."""
    try:
        data = request.get_json()
        target_tier = data.get('tier', 'basic')
        duration_days = data.get('duration_days', 30)
        
        # Validate tier
        valid_tiers = ['free', 'basic', 'pro', 'enterprise']
        if target_tier not in valid_tiers:
            return jsonify({'error': f'Invalid tier. Must be one of: {valid_tiers}'}), 400
        
        user = g.current_user
        user_id = user['id']
        
        # Calculate billing dates
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=duration_days)
        
        # Update user subscription tier
        user_update = {
            'subscription_tier': target_tier,
            'updated_at': start_date.isoformat()
        }
        
        result = supabase_service.client.table('users').update(user_update).eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to update user tier'}), 500
        
        # Create/update subscription record
        subscription_data = {
            'id': f"manual_{user_id}_{target_tier}",
            'user_id': user_id,
            'tier': target_tier,
            'status': 'active',
            'payment_id': 'manual_upgrade',
            'amount': 0,  # Manual upgrade, no payment
            'currency': 'INR',
            'billing_cycle_start': start_date.isoformat(),
            'billing_cycle_end': end_date.isoformat(),
            'created_at': start_date.isoformat(),
            'updated_at': start_date.isoformat()
        }
        
        # Try to update existing subscription, if not exists, insert new
        existing_sub = supabase_service.get_user_subscription(user_id)
        if existing_sub:
            sub_result = supabase_service.client.table('subscriptions').update(subscription_data).eq('user_id', user_id).execute()
        else:
            sub_result = supabase_service.client.table('subscriptions').insert(subscription_data).execute()
        
        logger.info(f"User {user['email']} manually upgraded to {target_tier} tier")
        
        return jsonify({
            'success': True,
            'message': f'Successfully upgraded to {target_tier} tier',
            'user': {
                'id': user_id,
                'email': user['email'],
                'subscription_tier': target_tier
            },
            'subscription': {
                'tier': target_tier,
                'status': 'active',
                'billing_cycle_start': start_date.isoformat(),
                'billing_cycle_end': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Manual upgrade error: {str(e)}")
        return jsonify({'error': 'Upgrade failed'}), 500

@manual_bp.route('/downgrade-user', methods=['POST'])
@supabase_auth_required
def manual_downgrade_user():
    """Manually downgrade a user back to free tier."""
    try:
        user = g.current_user
        user_id = user['id']
        
        # Update user to free tier
        user_update = {
            'subscription_tier': 'free',
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = supabase_service.client.table('users').update(user_update).eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to downgrade user'}), 500
        
        # Update subscription to inactive
        sub_update = {
            'status': 'cancelled',
            'updated_at': datetime.utcnow().isoformat()
        }
        
        supabase_service.client.table('subscriptions').update(sub_update).eq('user_id', user_id).execute()
        
        logger.info(f"User {user['email']} downgraded to free tier")
        
        return jsonify({
            'success': True,
            'message': 'Successfully downgraded to free tier',
            'user': {
                'id': user_id,
                'email': user['email'],
                'subscription_tier': 'free'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Manual downgrade error: {str(e)}")
        return jsonify({'error': 'Downgrade failed'}), 500

@manual_bp.route('/subscription-status', methods=['GET'])
@supabase_auth_required
def get_subscription_status():
    """Get current subscription status for logged-in user."""
    try:
        user = g.current_user
        subscription = supabase_service.get_user_subscription(user['id'])
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'subscription_tier': user['subscription_tier']
            },
            'subscription': subscription
        }), 200
        
    except Exception as e:
        logger.error(f"Get subscription status error: {str(e)}")
        return jsonify({'error': 'Failed to get subscription status'}), 500
