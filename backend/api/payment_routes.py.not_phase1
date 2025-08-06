"""
Razorpay Payment Integration for AI Profanity Filter SaaS
Production-ready payment processing with webhooks and subscription management.
"""

import os
import logging
import hmac
import hashlib
import razorpay
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models.saas_models import db, User, Subscription

# Configure logging
logger = logging.getLogger(__name__)

# Razorpay client initialization
razorpay_client = razorpay.Client(
    auth=(
        os.getenv('RAZORPAY_KEY_ID', 'rzp_test_your_key_id'),
        os.getenv('RAZORPAY_KEY_SECRET', 'your_key_secret')
    )
)

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Subscription plan configurations
SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'Basic Plan',
        'amount': 99900,  # Amount in paise (₹999)
        'currency': 'INR',
        'interval': 1,
        'period': 'monthly',
        'features': ['100 videos/month', '500MB files', 'API access', 'Email support']
    },
    'pro': {
        'name': 'Professional Plan',
        'amount': 299900,  # Amount in paise (₹2999)
        'currency': 'INR',
        'interval': 1,
        'period': 'monthly',
        'features': ['500 videos/month', '1GB files', 'Priority processing', 'Custom wordlists', 'Phone support']
    },
    'enterprise': {
        'name': 'Enterprise Plan',
        'amount': 999900,  # Amount in paise (₹9999)
        'currency': 'INR',
        'interval': 1,
        'period': 'monthly',
        'features': ['Unlimited videos', '5GB files', 'Dedicated support', 'Custom integration', 'White-label option']
    }
}

@payment_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get available subscription plans with Razorpay pricing."""
    try:
        plans_response = {}
        for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
            plans_response[plan_id] = {
                'id': plan_id,
                'name': plan_data['name'],
                'price': plan_data['amount'] / 100,  # Convert to rupees
                'currency': plan_data['currency'],
                'billing_cycle': f"{plan_data['interval']} {plan_data['period']}",
                'features': plan_data['features']
            }
        
        return jsonify({
            'plans': plans_response,
            'currency': 'INR',
            'payment_methods': ['card', 'netbanking', 'wallet', 'upi'],
            'test_mode': os.getenv('RAZORPAY_KEY_ID', '').startswith('rzp_test_')
        }), 200
        
    except Exception as e:
        logger.error(f"Get plans error: {str(e)}")
        return jsonify({'error': 'Failed to fetch plans'}), 500

@payment_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    """Create Razorpay order for subscription payment."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if plan_id not in SUBSCRIPTION_PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan = SUBSCRIPTION_PLANS[plan_id]
        
        # Create Razorpay order
        order_data = {
            'amount': plan['amount'],
            'currency': plan['currency'],
            'receipt': f"order_rcptid_{user_id}_{datetime.utcnow().timestamp()}",
            'payment_capture': 1,
            'notes': {
                'user_id': str(user_id),
                'plan_id': plan_id,
                'user_email': user.email
            }
        }
        
        razorpay_order = razorpay_client.order.create(order_data)
        
        # Create pending subscription record
        subscription = Subscription(
            user_id=user.id,
            plan_name=plan_id,
            plan_price=plan['amount'] / 100,
            status='pending',
            razorpay_order_id=razorpay_order['id']
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key_id': os.getenv('RAZORPAY_KEY_ID'),
            'subscription_id': subscription.id,
            'plan': {
                'name': plan['name'],
                'features': plan['features']
            },
            'user': {
                'name': user.full_name or user.email,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create order error: {str(e)}")
        return jsonify({'error': 'Failed to create payment order'}), 500

@payment_bp.route('/verify-payment', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify payment signature and activate subscription."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({'error': 'Missing payment details'}), 400
        
        # Verify signature
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        signature_payload = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            key_secret.encode(),
            signature_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, razorpay_signature):
            return jsonify({'error': 'Invalid payment signature'}), 400
        
        # Find subscription
        subscription = Subscription.query.filter_by(
            razorpay_order_id=razorpay_order_id,
            user_id=user.id
        ).first()
        
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Activate subscription
        subscription.status = 'active'
        subscription.is_active = True
        subscription.razorpay_payment_id = razorpay_payment_id
        subscription.start_date = datetime.utcnow()
        subscription.end_date = datetime.utcnow() + timedelta(days=30)
        
        # Update user subscription tier
        user.subscription_tier = subscription.plan_name
        
        db.session.commit()
        
        logger.info(f"Payment verified and subscription activated for user: {user.email}")
        
        return jsonify({
            'message': 'Payment verified and subscription activated',
            'subscription': subscription.to_dict(),
            'user': {
                'subscription_tier': user.subscription_tier,
                'plan_features': SUBSCRIPTION_PLANS[subscription.plan_name]['features']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Verify payment error: {str(e)}")
        return jsonify({'error': 'Payment verification failed'}), 500

@payment_bp.route('/webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhooks for payment events."""
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
            payment_id = payment_data.get('id')
            
            # Find and activate subscription
            subscription = Subscription.query.filter_by(razorpay_order_id=order_id).first()
            if subscription and subscription.status == 'pending':
                subscription.status = 'active'
                subscription.is_active = True
                subscription.razorpay_payment_id = payment_id
                subscription.start_date = datetime.utcnow()
                subscription.end_date = datetime.utcnow() + timedelta(days=30)
                
                # Update user subscription tier
                user = subscription.user
                user.subscription_tier = subscription.plan_name
                
                db.session.commit()
                
                logger.info(f"Webhook: Payment captured for subscription: {subscription.id}")
        
        elif event_type == 'payment.failed':
            # Handle failed payment
            payment_data = event['payload']['payment']['entity']
            order_id = payment_data.get('order_id')
            
            subscription = Subscription.query.filter_by(razorpay_order_id=order_id).first()
            if subscription:
                subscription.status = 'failed'
                db.session.commit()
                
                logger.info(f"Webhook: Payment failed for subscription: {subscription.id}")
        
        elif event_type == 'subscription.cancelled':
            # Handle subscription cancellation
            subscription_data = event['payload']['subscription']['entity']
            razorpay_sub_id = subscription_data.get('id')
            
            subscription = Subscription.query.filter_by(razorpay_subscription_id=razorpay_sub_id).first()
            if subscription:
                subscription.cancel()
                
                # Downgrade user to free tier
                user = subscription.user
                user.subscription_tier = 'free'
                
                db.session.commit()
                
                logger.info(f"Webhook: Subscription cancelled: {subscription.id}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@payment_bp.route('/subscription/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user's active subscription."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find active subscription
        subscription = user.get_active_subscription()
        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Cancel subscription
        subscription.cancel()
        
        # Downgrade user to free tier
        user.subscription_tier = 'free'
        
        db.session.commit()
        
        logger.info(f"Subscription cancelled for user: {user.email}")
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'effective_date': subscription.cancelled_at.isoformat(),
            'access_until': subscription.end_date.isoformat() if subscription.end_date else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cancel subscription error: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500

@payment_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get user's payment history and invoices."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's subscription history
        subscriptions = Subscription.query.filter_by(user_id=user.id).order_by(
            Subscription.created_at.desc()
        ).all()
        
        invoices = []
        for subscription in subscriptions:
            if subscription.razorpay_payment_id:
                try:
                    # Fetch payment details from Razorpay
                    payment = razorpay_client.payment.fetch(subscription.razorpay_payment_id)
                    
                    invoices.append({
                        'id': subscription.id,
                        'plan_name': subscription.plan_name,
                        'amount': subscription.plan_price,
                        'currency': 'INR',
                        'status': subscription.status,
                        'payment_date': subscription.start_date.isoformat() if subscription.start_date else None,
                        'billing_period': {
                            'start': subscription.start_date.isoformat() if subscription.start_date else None,
                            'end': subscription.end_date.isoformat() if subscription.end_date else None
                        },
                        'razorpay_payment_id': subscription.razorpay_payment_id,
                        'payment_method': payment.get('method', 'unknown')
                    })
                except Exception as e:
                    logger.error(f"Failed to fetch payment details: {str(e)}")
                    # Add basic invoice info even if Razorpay fetch fails
                    invoices.append({
                        'id': subscription.id,
                        'plan_name': subscription.plan_name,
                        'amount': subscription.plan_price,
                        'currency': 'INR',
                        'status': subscription.status,
                        'payment_date': subscription.start_date.isoformat() if subscription.start_date else None,
                        'razorpay_payment_id': subscription.razorpay_payment_id
                    })
        
        return jsonify({
            'invoices': invoices,
            'total_invoices': len(invoices)
        }), 200
        
    except Exception as e:
        logger.error(f"Get invoices error: {str(e)}")
        return jsonify({'error': 'Failed to fetch invoices'}), 500
