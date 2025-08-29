"""
Razorpay Payment Integration for AI Profanity Filter SaaS
Handles payment webhooks and user tier upgrades.
"""

import os
import hmac
import hashlib
import json
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

# Create payment blueprint
payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Plan mapping
PLAN_MAPPING = {
    'test': {
        'tier': 'basic',
        'duration_days': 1,
        'price': 1  # ₹1 for testing
    },
    'upgradebasic': {
        'tier': 'basic',
        'duration_days': 30,
        'price': 399  # ₹399
    },
    'upgradepro': {
        'tier': 'pro', 
        'duration_days': 30,
        'price': 999  # ₹999
    },
    'upgradeenterprise': {
        'tier': 'enterprise',
        'duration_days': 30,
        'price': 1999  # ₹1999
    }
}

def verify_razorpay_signature(payload, signature, secret):
    """Verify Razorpay webhook signature for security."""
    try:
        # Create HMAC signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        return False

@payment_bp.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay payment webhooks."""
    try:
        # Get webhook secret from environment
        webhook_secret = os.environ.get('RAZORPAY_WEBHOOK_SECRET')
        if not webhook_secret:
            logger.error("RAZORPAY_WEBHOOK_SECRET not configured")
            return jsonify({'error': 'Webhook secret not configured'}), 500
        
        # Get signature from headers
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            logger.warning("Missing Razorpay signature")
            return jsonify({'error': 'Missing signature'}), 400
        
        # Get payload
        payload = request.get_data()
        
        # Verify signature
        if not verify_razorpay_signature(payload, signature, webhook_secret):
            logger.warning("Invalid Razorpay signature")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse webhook data
        webhook_data = request.get_json()
        event = webhook_data.get('event')
        
        logger.info(f"Received Razorpay webhook: {event}")
        
        # Handle payment success
        if event == 'payment.captured':
            return handle_payment_success(webhook_data)
        elif event == 'payment.failed':
            return handle_payment_failed(webhook_data)
        else:
            logger.info(f"Unhandled webhook event: {event}")
            return jsonify({'status': 'ignored'}), 200
            
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def handle_payment_success(webhook_data):
    """Handle successful payment and upgrade user."""
    try:
        payment = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
        
        # Extract payment details
        payment_id = payment.get('id')
        amount = payment.get('amount', 0) / 100  # Convert from paise to rupees
        currency = payment.get('currency', 'INR')
        
        # Get notes from payment (should contain user info)
        notes = payment.get('notes', {})
        user_email = notes.get('user_email')
        plan_id = notes.get('plan_id')
        
        # If no user info in notes, try to extract from order details
        order_id = payment.get('order_id')
        if not user_email and order_id:
            # Parse order_id which might contain user info: user_email_planid
            try:
                parts = order_id.split('_')
                if len(parts) >= 3 and '@' in parts[0]:
                    user_email = parts[0]
                    plan_id = parts[-1]
            except:
                pass
        
        logger.info(f"Payment success: {payment_id}, Amount: {amount}, User: {user_email}, Plan: {plan_id}")
        
        if not user_email:
            logger.error("No user email found in payment data")
            return jsonify({'error': 'Missing user information'}), 400
        
        # If no plan_id, determine from amount
        if not plan_id:
            if amount == 399:
                plan_id = 'upgradebasic'
            elif amount == 999:
                plan_id = 'upgradepro'
            elif amount == 1999:
                plan_id = 'upgradeenterprise'
            else:
                logger.error(f"Cannot determine plan from amount: {amount}")
                return jsonify({'error': 'Unknown payment amount'}), 400
        
        # Get plan details
        plan_info = PLAN_MAPPING.get(plan_id)
        if not plan_info:
            logger.error(f"Unknown plan_id: {plan_id}")
            return jsonify({'error': 'Unknown plan'}), 400
        
        # Verify payment amount matches plan price
        if abs(amount - plan_info['price']) > 1:  # Allow 1 rupee difference for rounding
            logger.warning(f"Amount mismatch: expected {plan_info['price']}, got {amount}. Proceeding anyway.")
        
        # Get user
        user = supabase_service.get_user_by_email(user_email)
        if not user:
            logger.error(f"User not found: {user_email}")
            return jsonify({'error': 'User not found'}), 404
        
        # Upgrade user subscription
        upgrade_result = upgrade_user_subscription(
            user['id'], 
            plan_info['tier'],
            plan_info['duration_days'],
            payment_id,
            amount
        )
        
        if upgrade_result['success']:
            logger.info(f"User {user_email} upgraded to {plan_info['tier']} successfully")
            return jsonify({'status': 'success', 'message': 'User upgraded successfully'}), 200
        else:
            logger.error(f"Failed to upgrade user {user_email}: {upgrade_result['error']}")
            return jsonify({'error': 'Upgrade failed'}), 500
            
    except Exception as e:
        logger.error(f"Payment success handling error: {str(e)}")
        return jsonify({'error': 'Payment processing failed'}), 500

def handle_payment_failed(webhook_data):
    """Handle failed payment."""
    try:
        payment = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
        payment_id = payment.get('id')
        
        logger.info(f"Payment failed: {payment_id}")
        
        # Could store failed payment for analytics/retry
        # For now, just log it
        
        return jsonify({'status': 'logged'}), 200
        
    except Exception as e:
        logger.error(f"Payment failure handling error: {str(e)}")
        return jsonify({'error': 'Failed payment processing error'}), 500

def upgrade_user_subscription(user_id, tier, duration_days, payment_id, amount):
    """Upgrade user to paid subscription tier."""
    try:
        # Calculate billing dates
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=duration_days)
        
        # Update user subscription tier
        user_update = {
            'subscription_tier': tier,
            'updated_at': start_date.isoformat()
        }
        
        result = supabase_service.client.table('users').update(user_update).eq('id', user_id).execute()
        
        if not result.data:
            return {'success': False, 'error': 'Failed to update user tier'}
        
        # Create subscription record
        subscription_data = {
            'id': f"sub_{payment_id}",
            'user_id': user_id,
            'tier': tier,
            'status': 'active',
            'payment_id': payment_id,
            'amount': amount,
            'currency': 'INR',
            'billing_cycle_start': start_date.isoformat(),
            'billing_cycle_end': end_date.isoformat(),
            'created_at': start_date.isoformat(),
            'updated_at': start_date.isoformat()
        }
        
        sub_result = supabase_service.client.table('subscriptions').insert(subscription_data).execute()
        
        logger.info(f"User {user_id} upgraded to {tier} tier until {end_date.strftime('%Y-%m-%d')}")
        
        return {
            'success': True,
            'subscription': sub_result.data[0] if sub_result.data else None
        }
        
    except Exception as e:
        logger.error(f"Subscription upgrade error: {str(e)}")
        return {'success': False, 'error': str(e)}

@payment_bp.route('/plans', methods=['GET'])
def get_payment_plans():
    """Get available payment plans."""
    try:
        plans = {}
        for plan_id, plan_info in PLAN_MAPPING.items():
            plans[plan_id] = {
                'tier': plan_info['tier'],
                'price': plan_info['price'],
                'duration_days': plan_info['duration_days'],
                'currency': 'INR'
            }
        
        return jsonify({'plans': plans}), 200
        
    except Exception as e:
        logger.error(f"Get plans error: {str(e)}")
        return jsonify({'error': 'Failed to get plans'}), 500

@payment_bp.route('/status/<user_id>', methods=['GET'])
def get_payment_status(user_id):
    """Get user's payment/subscription status."""
    try:
        # Get user
        user = supabase_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get active subscription
        subscription = supabase_service.get_user_subscription(user_id)
        
        return jsonify({
            'user_tier': user['subscription_tier'],
            'subscription': subscription
        }), 200
        
    except Exception as e:
        logger.error(f"Get payment status error: {str(e)}")
        return jsonify({'error': 'Failed to get payment status'}), 500

@payment_bp.route('/create-order', methods=['POST'])
def create_payment_order():
    """Create a payment order with user information for proper webhook handling."""
    try:
        from api.supabase_routes import supabase_auth_required
        from flask import g
        
        # This endpoint requires authentication
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        
        # Verify JWT token
        verify_jwt_in_request(locations=['cookies'])
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get user from database
        user = supabase_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Get plan from request
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if not plan_id or plan_id not in PLAN_MAPPING:
            return jsonify({'error': 'Invalid plan_id'}), 400
        
        plan_info = PLAN_MAPPING[plan_id]
        
        # Create order ID with user info for webhook processing
        order_id = f"{user['email']}_{plan_id}_{user_id[:8]}"
        
        # Return payment information
        payment_info = {
            'order_id': order_id,
            'amount': plan_info['price'],
            'currency': 'INR',
            'plan': plan_info['tier'],
            'user_email': user['email'],
            'payment_link': f"https://rzp.io/rzp/{plan_id}",
            'notes': {
                'user_email': user['email'],
                'plan_id': plan_id,
                'user_id': user_id
            }
        }
        
        logger.info(f"Payment order created for user {user['email']}, plan {plan_id}")
        
        return jsonify({
            'success': True,
            'payment_info': payment_info
        }), 200
        
    except Exception as e:
        logger.error(f"Create payment order error: {str(e)}")
        return jsonify({'error': 'Failed to create payment order'}), 500
