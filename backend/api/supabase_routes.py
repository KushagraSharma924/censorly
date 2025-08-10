"""
Supabase-based API Routes for AI Profanity Filter SaaS Platform
Complete replacement for SQLAlchemy-based routes using pure Supabase.
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging
from datetime import datetime, timedelta
import uuid
import json
import jwt
import time
from collections import defaultdict

from services.supabase_service import supabase_service

# Import rate limiter
try:
    from services.rate_limiter import RateLimiter
    rate_limiter = RateLimiter()
except ImportError:
    rate_limiter = None

# Simple in-memory rate limiting storage
_rate_limit_storage = defaultdict(list)

logger = logging.getLogger(__name__)

# Create blueprint
supabase_bp = Blueprint('supabase_api', __name__, url_prefix='/api')

# Rate limiting will be handled by Supabase Edge Functions or external service
# For now, we'll implement basic rate limiting

def supabase_auth_required(f):
    """Decorator for JWT authentication (no Supabase Auth)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Manually decode JWT token
            import jwt
            from flask import current_app
            
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            user_id = payload.get('sub')  # JWT standard claim for subject
            
            if not user_id:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Get user data from database
            user_data = supabase_service.get_user_by_id(user_id)
            if not user_data:
                return jsonify({'error': 'User not found'}), 404
            
            # Add user data to request context
            request.current_user = user_data
            request.user_id = user_id
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def api_key_required(f):
    """Decorator for API key authentication with rate limiting."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Verify API key
        key_data = supabase_service.verify_api_key(api_key)
        if not key_data:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Check rate limiting
        if rate_limiter:
            try:
                # Determine endpoint type based on URL
                endpoint_type = 'general'
                if 'create_job' in request.endpoint and request.method == 'POST':
                    endpoint_type = 'processing'
                elif 'upload' in request.endpoint:
                    endpoint_type = 'upload'
                
                logger.info(f"Rate limiting check: endpoint={request.endpoint}, method={request.method}, type={endpoint_type}")
                
                # Get user data to determine subscription tier
                user_data = supabase_service.get_user_by_id(key_data['user_id'])
                if not user_data:
                    logger.error(f"User not found for API key {key_data['id']}")
                    return jsonify({'error': 'User not found'}), 404
                
                # Get subscription tier (default to 'free' if not set)
                subscription_tier = user_data.get('subscription_tier', 'free')
                
                # Define monthly limits
                tier_limits = {
                    'free': {
                        'general': 50,
                        'processing': 10,
                        'upload': 10
                    },
                    'basic': {
                        'general': 100,
                        'processing': 40,
                        'upload': 40
                    },
                    'premium': {
                        'general': 1000,
                        'processing': 500,
                        'upload': 500
                    }
                }
                
                # Get the limit for current tier and endpoint type
                limits = tier_limits.get(subscription_tier, tier_limits['free'])
                monthly_limit = limits.get(endpoint_type, limits['general'])
                
                # Check monthly usage from database
                api_key_id = key_data['id']
                user_id = key_data['user_id']
                
                # Get current month start
                now = datetime.utcnow()
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                # Count API calls for this month by checking job creation (for processing) or general API usage
                if endpoint_type == 'processing':
                    # Count jobs created this month for processing endpoints
                    monthly_usage_result = supabase_service.client.table("jobs").select("id").eq("user_id", user_id).gte("created_at", month_start.isoformat()).execute()
                    current_usage = len(monthly_usage_result.data or [])
                else:
                    # For general endpoints, we'll track usage in the API key usage_count
                    # Get current usage count for this month (simplified - using total usage)
                    current_usage = key_data.get('usage_count', 0)
                    # Note: In a production system, you'd want to track monthly usage separately
                
                logger.info(f"Monthly limit check: tier={subscription_tier}, endpoint={endpoint_type}, limit={monthly_limit}, current={current_usage}")
                
                if current_usage >= monthly_limit:
                    # Calculate days until next month
                    next_month = (month_start + timedelta(days=32)).replace(day=1)
                    days_until_reset = (next_month - now).days + 1
                    
                    logger.warning(f"Monthly limit exceeded for API key {api_key_id}: {current_usage}/{monthly_limit}")
                    return jsonify({
                        'error': 'Monthly limit exceeded',
                        'message': f'Monthly limit exceeded. Limit: {monthly_limit} {endpoint_type} calls per month for {subscription_tier} tier.',
                        'retry_after': days_until_reset * 24 * 60 * 60,  # seconds until reset
                        'current_usage': current_usage,
                        'limit': monthly_limit,
                        'tier': subscription_tier,
                        'reset_date': next_month.isoformat(),
                        'endpoint_type': endpoint_type
                    }), 429
                
                logger.info(f"Monthly limit passed: {current_usage + 1}/{monthly_limit}")
                    
            except Exception as e:
                logger.error(f"Rate limiting error: {str(e)}")
                # Continue without rate limiting if there's an error
        else:
            logger.warning("Rate limiter not available - skipping rate limiting check")
        
        # Get user data
        user_data = supabase_service.get_user_by_id(key_data['user_id'])
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Increment API key usage count for actual operations
        supabase_service.increment_api_key_usage(key_data['id'])
        
        request.current_user = user_data
        request.current_api_key = key_data
        return f(*args, **kwargs)
    
    return decorated_function

# Authentication Routes
@supabase_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Check if user already exists
        existing_user = supabase_service.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user
        result = supabase_service.create_user(email, password, full_name)
        
        if result['success']:
            # Auto-login after registration by authenticating the new user
            auth_result = supabase_service.authenticate_user(email, password)
            
            if auth_result['success']:
                logger.info(f"New user registered and logged in: {email}")
                return jsonify({
                    'message': 'User registered successfully',
                    'user': {
                        'id': result['user']['id'],
                        'email': result['user']['email'],
                        'full_name': result['user']['full_name'],
                        'subscription_tier': result['user']['subscription_tier']
                    },
                    'tokens': {
                        'access_token': auth_result['access_token'],
                        'refresh_token': auth_result['refresh_token']
                    }
                }), 201
            else:
                # Registration succeeded but auto-login failed
                logger.warning(f"Registration succeeded but auto-login failed for: {email}")
                return jsonify({
                    'message': 'User registered successfully. Please login.',
                    'user': {
                        'id': result['user']['id'],
                        'email': result['user']['email'],
                        'full_name': result['user']['full_name'],
                        'subscription_tier': result['user']['subscription_tier']
                    }
                }), 201
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@supabase_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        result = supabase_service.authenticate_user(email, password)
        
        if result['success']:
            logger.info(f"User logged in: {email}")
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': result['user']['id'],
                    'email': result['user']['email'],
                    'full_name': result['user']['full_name'],
                    'subscription_tier': result['user']['subscription_tier']
                },
                'tokens': {
                    'access_token': result['access_token'],
                    'refresh_token': result.get('refresh_token', result['access_token'])  # Use access token as fallback
                }
            }), 200
        else:
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@supabase_bp.route('/auth/logout', methods=['POST'])
@supabase_auth_required
def logout():
    """User logout."""
    try:
        # In a stateless JWT setup, logout is handled client-side
        # by removing the token. We can optionally blacklist tokens here.
        
        user = request.current_user
        logger.info(f"User logged out: {user['email']}")
        
        return jsonify({
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@supabase_bp.route('/auth/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token validity."""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Verify token
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('sub')
            
            if not user_id:
                return jsonify({'error': 'Invalid token payload'}), 401
            
            # Get user data
            user_data = supabase_service.get_user_by_id(user_id)
            if not user_data:
                return jsonify({'error': 'User not found'}), 401
            
            return jsonify({
                'valid': True,
                'user': {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'name': user_data['full_name'],
                    'subscription_tier': user_data['subscription_tier']
                }
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired', 'valid': False}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token', 'valid': False}), 401
            
    except Exception as e:
        logger.error(f"Verify token error: {str(e)}")
        return jsonify({'error': 'Token verification failed'}), 500

@supabase_bp.route('/auth/refresh', methods=['POST'])
@supabase_auth_required
def refresh_token():
    """Refresh JWT token."""
    try:
        user = request.current_user
        
        # Create new access token using JWT
        payload = {
            'sub': user['id'],
            'email': user['email'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        new_access_token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'access_token': new_access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['full_name'],
                'subscription_tier': user['subscription_tier']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500

@supabase_bp.route('/test/profile', methods=['GET'])
def test_profile():
    """Test endpoint to return real user data without authentication (for debugging)."""
    try:
        # Get the real user from Supabase
        user = supabase_service.get_user_by_email('kush090605@gmail.com')
        if user:
            return jsonify({
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['full_name'],  # Frontend expects 'name'
                    'full_name': user['full_name'],
                    'subscription_tier': user['subscription_tier'],
                    'subscription_status': 'active' if user.get('is_active', True) else 'inactive',
                    'videos_processed': user.get('videos_processed', 0),
                    'total_processing_time': user.get('total_processing_time', 0),
                    'is_verified': user.get('is_verified', False),
                    'created_at': user['created_at']
                }
            })
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Test profile error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@supabase_bp.route('/auth/profile', methods=['GET'])
# @supabase_auth_required  # Temporarily disabled for testing
def get_profile():
    """Get user profile."""
    try:
        # Temporarily return the real user data for testing
        user = supabase_service.get_user_by_email('kush090605@gmail.com')
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        subscription = supabase_service.get_user_subscription(user['id'])
        
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['full_name'],  # Frontend expects 'name'
                'full_name': user['full_name'],  # Keep both for compatibility
                'profile_image_url': user.get('profile_image_url', ''),  # Add profile image
                'subscription_tier': user['subscription_tier'],
                'subscription_status': 'active' if user.get('is_active', True) else 'inactive',  # Add missing field
                'videos_processed': user.get('videos_processed', 0),
                'total_processing_time': user.get('total_processing_time', 0),
                'is_verified': user.get('is_verified', False),
                'created_at': user['created_at']
            },
            'subscription': subscription,
            'plan_limits': supabase_service.get_plan_limits(user['subscription_tier'])
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500

@supabase_bp.route('/auth/upload-profile-image', methods=['POST'])
@supabase_auth_required
def upload_profile_image():
    """Upload and update user profile image using Supabase Storage."""
    try:
        user = request.current_user
        
        # Check if file is in request
        if 'profile_image' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['profile_image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400
        
        # Validate file size (5MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'error': 'File too large. Maximum size is 5MB'}), 400
        
        # Generate unique filename
        unique_filename = f"profile_images/{user['id']}/{uuid.uuid4()}.{file_extension}"
        
        try:
            # Read file content
            file_content = file.read()
            
            # Upload to Supabase Storage
            storage_response = supabase_service.client.storage.from_('profile-images').upload(
                path=unique_filename,
                file=file_content,
                file_options={
                    'content-type': f'image/{file_extension}',
                    'upsert': True  # Replace if exists
                }
            )
            
            if hasattr(storage_response, 'error') and storage_response.error:
                logger.error(f"Supabase storage upload error: {storage_response.error}")
                return jsonify({'error': 'Failed to upload image to storage'}), 500
            
            # Get public URL for the uploaded image
            public_url_response = supabase_service.client.storage.from_('profile-images').get_public_url(unique_filename)
            
            if not public_url_response:
                logger.error("Failed to get public URL for uploaded image")
                return jsonify({'error': 'Failed to get image URL'}), 500
            
            image_url = public_url_response
            
            # Clean up old profile image if exists
            try:
                if user.get('profile_image_url') and 'profile-images' in user.get('profile_image_url', ''):
                    # Extract old file path from URL
                    old_url = user['profile_image_url']
                    if '/profile-images/' in old_url:
                        old_path = old_url.split('/profile-images/')[1].split('?')[0]  # Remove query params
                        if old_path != unique_filename:  # Don't delete if it's the same file
                            supabase_service.client.storage.from_('profile-images').remove([f"profile_images/{old_path}"])
                            logger.info(f"Cleaned up old profile image: profile_images/{old_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup old profile image: {cleanup_error}")
                # Continue anyway, old file cleanup is not critical
            
            # Update user profile with image URL
            update_result = supabase_service.client.table("users").update({
                "profile_image_url": image_url,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user['id']).execute()
            
            if update_result.data:
                logger.info(f"Profile image updated for user {user['id']}: {unique_filename}")
                return jsonify({
                    'message': 'Profile image updated successfully',
                    'profile_image_url': image_url,
                    'file_path': unique_filename
                }), 200
            else:
                # If database update fails, try to clean up the uploaded file
                try:
                    supabase_service.client.storage.from_('profile-images').remove([unique_filename])
                except:
                    pass
                return jsonify({'error': 'Failed to update profile in database'}), 500
                
        except Exception as storage_error:
            logger.error(f"Storage operation error: {str(storage_error)}")
            return jsonify({'error': f'Storage error: {str(storage_error)}'}), 500
            
    except Exception as e:
        logger.error(f"Upload profile image error: {str(e)}")
        return jsonify({'error': 'Failed to upload profile image'}), 500

@supabase_bp.route('/auth/delete-profile-image', methods=['DELETE'])
@supabase_auth_required
def delete_profile_image():
    """Delete user's profile image."""
    try:
        user = request.current_user
        
        # Check if user has a profile image
        if not user.get('profile_image_url'):
            return jsonify({'error': 'No profile image to delete'}), 400
        
        # Extract file path from URL if it's a Supabase Storage URL
        image_url = user['profile_image_url']
        if '/profile-images/' in image_url:
            try:
                # Extract file path
                file_path = image_url.split('/profile-images/')[1].split('?')[0]  # Remove query params
                full_path = f"profile_images/{file_path}"
                
                # Delete from storage
                delete_response = supabase_service.client.storage.from_('profile-images').remove([full_path])
                
                logger.info(f"Deleted profile image from storage: {full_path}")
            except Exception as storage_error:
                logger.warning(f"Failed to delete image from storage: {storage_error}")
                # Continue anyway, we'll still clear the URL from database
        
        # Update user profile to remove image URL
        update_result = supabase_service.client.table("users").update({
            "profile_image_url": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user['id']).execute()
        
        if update_result.data:
            logger.info(f"Profile image deleted for user {user['id']}")
            return jsonify({
                'message': 'Profile image deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile in database'}), 500
            
    except Exception as e:
        logger.error(f"Delete profile image error: {str(e)}")
        return jsonify({'error': 'Failed to delete profile image'}), 500

@supabase_bp.route('/auth/usage', methods=['GET'])
# @supabase_auth_required  # Temporarily disabled for testing
def get_usage_stats():
    """Get user usage statistics."""
    try:
        # Temporarily get the real user for testing
        user = supabase_service.get_user_by_email('kush090605@gmail.com')
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user_id = user['id']
        subscription_tier = user.get('subscription_tier', 'free')
        
        # Get current month start
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Define tier limits
        tier_limits = {
            'free': {
                'general': 50,
                'processing': 10,
                'upload': 10,
                'max_api_keys': 3
            },
            'basic': {
                'general': 100,
                'processing': 40,
                'upload': 40,
                'max_api_keys': 10
            },
            'premium': {
                'general': 1000,
                'processing': 500,
                'upload': 500,
                'max_api_keys': 50
            }
        }
        
        limits = tier_limits.get(subscription_tier, tier_limits['free'])
        
        # Count processing calls (jobs created this month)
        processing_usage_result = supabase_service.client.table("jobs").select("id").eq("user_id", user_id).gte("created_at", month_start.isoformat()).execute()
        processing_usage = len(processing_usage_result.data or [])
        
        # Count API keys
        api_keys_result = supabase_service.client.table("api_keys").select("id").eq("user_id", user_id).eq("is_active", True).execute()
        api_keys_count = len(api_keys_result.data or [])
        
        # Calculate next month reset date
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        return jsonify({
            'usage': {
                'processing': {
                    'current': processing_usage,
                    'limit': limits['processing'],
                    'percentage': round((processing_usage / limits['processing']) * 100, 1) if limits['processing'] > 0 else 0
                },
                'upload': {
                    'current': processing_usage,  # Website uploads use the same job creation count
                    'limit': limits['upload'],
                    'percentage': round((processing_usage / limits['upload']) * 100, 1) if limits['upload'] > 0 else 0
                },
                'general': {
                    'current': 0,  # Would need to track general API calls separately
                    'limit': limits['general'],
                    'percentage': 0
                },
                'api_keys': {
                    'current': api_keys_count,
                    'limit': limits['max_api_keys'],
                    'percentage': round((api_keys_count / limits['max_api_keys']) * 100, 1) if limits['max_api_keys'] > 0 else 0
                }
            },
            'limits': limits,
            'tier': subscription_tier,
            'reset_date': next_month.isoformat(),
            'current_period': {
                'start': month_start.isoformat(),
                'end': next_month.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get usage stats error: {str(e)}")
        return jsonify({'error': 'Failed to get usage statistics'}), 500

# Alias endpoint for usage stats (compatibility)
@supabase_bp.route('/usage/stats', methods=['GET', 'OPTIONS'])
# @supabase_auth_required  # Temporarily disabled for testing
def get_usage_stats_alias():
    """Alias for get_usage_stats to support different frontend calls."""
    return get_usage_stats()

# API Key Management
@supabase_bp.route('/keys', methods=['GET'])
@supabase_auth_required
def list_api_keys():
    """List user's API keys."""
    try:
        user = request.current_user
        api_keys = supabase_service.get_user_api_keys(user['id'])
        
        # Remove sensitive data
        safe_keys = []
        for key in api_keys:
            safe_keys.append({
                'id': key['id'],
                'name': key['name'],
                'key_prefix': key['key_prefix'],
                'is_active': key['is_active'],
                'usage_count': key['usage_count'],
                'last_used': key['last_used'],
                'created_at': key['created_at']
            })
        
        return jsonify({'api_keys': safe_keys}), 200
        
    except Exception as e:
        logger.error(f"List API keys error: {str(e)}")
        return jsonify({'error': 'Failed to list API keys'}), 500

@supabase_bp.route('/keys', methods=['POST'])
@supabase_auth_required
def create_api_key():
    """Create a new API key."""
    try:
        user = request.current_user
        data = request.get_json()
        name = data.get('name', 'Unnamed Key').strip()
        
        if not name:
            return jsonify({'error': 'Key name is required'}), 400
        
        # Check API key limit based on subscription tier
        existing_keys = supabase_service.get_user_api_keys(user['id'])
        active_keys = [k for k in existing_keys if k['is_active']]
        
        # Define API key limits per tier
        subscription_tier = user.get('subscription_tier', 'free')
        tier_limits = {
            'free': 3,
            'basic': 10,
            'premium': 50
        }
        
        max_keys = tier_limits.get(subscription_tier, tier_limits['free'])
        
        if len(active_keys) >= max_keys:
            return jsonify({
                'error': 'Maximum API keys limit reached',
                'message': f'You can create maximum {max_keys} API keys on {subscription_tier} tier. You currently have {len(active_keys)} active keys.',
                'current_count': len(active_keys),
                'limit': max_keys,
                'tier': subscription_tier
            }), 400
        
        # Create API key
        result = supabase_service.create_api_key(user['id'], name)
        
        if result['success']:
            logger.info(f"New API key created for user: {user['email']}")
            return jsonify({
                'message': 'API key created successfully',
                'api_key': result['raw_key'],
                'key_info': {
                    'id': result['api_key']['id'],
                    'name': result['api_key']['name'],
                    'key_prefix': result['api_key']['key_prefix'],
                    'created_at': result['api_key']['created_at']
                }
            }), 201
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Create API key error: {str(e)}")
        return jsonify({'error': 'Failed to create API key'}), 500

@supabase_bp.route('/keys/<key_id>', methods=['DELETE'])
@supabase_auth_required
def delete_api_key(key_id):
    """Delete an API key."""
    try:
        user = request.current_user
        
        result = supabase_service.delete_api_key(key_id, user['id'])
        
        if result['success']:
            logger.info(f"API key deleted: {key_id}")
            return jsonify({'message': 'API key deleted successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Delete API key error: {str(e)}")
        return jsonify({'error': 'Failed to delete API key'}), 500

# Job Management
@supabase_bp.route('/jobs', methods=['GET'])
@supabase_auth_required
def list_jobs():
    """List user's jobs."""
    try:
        user = request.current_user
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = (page - 1) * limit
        
        jobs = supabase_service.get_user_jobs(user['id'], limit, offset)
        
        return jsonify({
            'jobs': jobs,
            'page': page,
            'limit': limit,
            'total': len(jobs)
        }), 200
        
    except Exception as e:
        logger.error(f"List jobs error: {str(e)}")
        return jsonify({'error': 'Failed to list jobs'}), 500

@supabase_bp.route('/jobs', methods=['POST'])
@api_key_required
def create_job():
    """Create a new job via API."""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        if not data.get('original_filename'):
            return jsonify({'error': 'Original filename is required'}), 400
        
        # Check plan limits
        plan_limits = supabase_service.get_plan_limits(user['subscription_tier'])
        
        # Check monthly limit
        if plan_limits['monthly_limit'] > 0:
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_jobs = supabase_service.client.table("jobs").select("id")\
                .eq("user_id", user['id'])\
                .gte("created_at", current_month_start.isoformat())\
                .execute()
            
            if len(monthly_jobs.data or []) >= plan_limits['monthly_limit']:
                return jsonify({'error': 'Monthly processing limit reached'}), 429
        
        # Create job
        job_data = {
            'original_filename': data.get('original_filename'),
            'file_size': data.get('file_size'),
            'duration': data.get('duration'),
            'censoring_mode': data.get('censoring_mode', 'beep'),
            'profanity_threshold': data.get('profanity_threshold', 0.8),
            'languages': json.dumps(data.get('languages', ['en'])),
            'status': 'pending'
        }
        
        result = supabase_service.create_job(user['id'], job_data)
        
        if result['success']:
            logger.info(f"New job created: {result['job']['id']}")
            return jsonify({
                'message': 'Job created successfully',
                'job': result['job']
            }), 201
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Create job error: {str(e)}")
        return jsonify({'error': 'Failed to create job'}), 500

@supabase_bp.route('/jobs/<job_id>', methods=['GET'])
@supabase_auth_required
def get_job(job_id):
    """Get job details."""
    try:
        user = request.current_user
        job = supabase_service.get_job(job_id, user['id'])
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job}), 200
        
    except Exception as e:
        logger.error(f"Get job error: {str(e)}")
        return jsonify({'error': 'Failed to get job'}), 500

# Health Check
@supabase_bp.route('/health', methods=['GET'])
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
                'supabase_auth',
                'api_key_management', 
                'subscription_billing',
                'multi_language_detection',
                'video_processing',
                'real_time_updates'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
