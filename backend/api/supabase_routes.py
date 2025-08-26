"""
Supabase-based API Routes for AI Profanity Filter SaaS Platform
Complete replacement for SQLAlchemy-based routes using pure Supabase.
"""

from flask import Blueprint, request, jsonify, current_app, send_file, make_response, g
from functools import wraps
import logging
from datetime import datetime, timedelta
import uuid
import json
import time
import os
import shutil
from pathlib import Path
from collections import defaultdict
from werkzeug.utils import secure_filename

from services.supabase_service import supabase_service
from utils.security_utils import secure_compare, verify_api_key

# Import security decorators
from decorators import secure_api_key_required

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
    """Decorator to require Supabase authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
            
            # Verify JWT token in request (handles cookies automatically)
            verify_jwt_in_request(locations=['cookies'])
            
            # Get user identity from token
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'error': 'Invalid token identity'}), 401
            
            # Get additional claims for validation
            claims = get_jwt()
            user_email = claims.get('email')
            
            if not user_email:
                return jsonify({'error': 'Invalid token claims'}), 401
                
            # Get user from Supabase using ID for efficiency
            user = supabase_service.get_user_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 401
                
            # Verify email matches (additional security)
            if user.get('email') != user_email:
                return jsonify({'error': 'Token-user mismatch'}), 401
                
            # Store user in g for use in the route
            g.current_user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            # Log authentication errors for debugging (production-safe)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Authentication failed: {type(e).__name__}: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def api_key_required(f):
    """Decorator for API key authentication with rate limiting and enhanced security."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        
        # Check if API key is present
        if not api_key:
            logger.warning("API request missing API key header")
            return jsonify({
                'error': 'API key required',
                'message': 'Please include your API key in the X-API-Key header'
            }), 401
        
        # Set a maximum length for API keys to prevent abuse
        if len(api_key) > 128:
            logger.warning("Oversized API key detected - possible attack")
            return jsonify({'error': 'Invalid API key format'}), 401
            
        # Verify API key with our enhanced secure verification
        key_data = supabase_service.verify_api_key(api_key)
        if not key_data:
            logger.warning("Invalid API key attempt")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or has been revoked'
            }), 401
        
        # Get user data
        user_data = supabase_service.get_user_by_id(key_data['user_id'])
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Increment API key usage count for actual operations
        supabase_service.increment_api_key_usage(key_data['id'])
        
        # Store user and key data in g for consistency with auth decorator
        g.current_user = user_data
        g.current_api_key = key_data
        return f(*args, **kwargs)
    
    return decorated_function

# Authentication Routes
try:
    from decorators.csrf_protection import csrf_protect, csrf_token_required
except ImportError:
    # Fallback decorators if CSRF protection module is not available
    def csrf_protect(f):
        return f
    def csrf_token_required(f):
        return f

@supabase_bp.route('/auth/register', methods=['POST'])
@csrf_protect
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
                
                # Create response
                response_data = {
                    'message': 'User registered successfully',
                    'user': {
                        'id': result['user']['id'],
                        'email': result['user']['email'],
                        'full_name': result['user']['full_name'],
                        'subscription_tier': result['user']['subscription_tier']
                    }
                    # Tokens no longer returned in response body
                }
                response = make_response(jsonify(response_data), 201)
                
                # Set httpOnly cookies for tokens
                max_age_access = 24 * 60 * 60  # 24 hours
                max_age_refresh = 30 * 24 * 60 * 60  # 30 days
                
                # Check if we're in production (use secure cookies only in production)
                is_production = os.getenv('RENDER_EXTERNAL_URL') is not None or 'onrender.com' in request.url_root
                
                response.set_cookie(
                    'access_token',
                    auth_result['access_token'],
                    max_age=max_age_access,
                    httponly=True,
                    secure=is_production,  # Only secure in production
                    samesite='None' if is_production else 'Strict'  # None required for cross-origin in production
                )
                
                if auth_result.get('refresh_token'):
                    response.set_cookie(
                        'refresh_token',
                        auth_result['refresh_token'],
                        max_age=max_age_refresh,
                        httponly=True,
                        secure=is_production,
                        samesite='None' if is_production else 'Strict'
                    )
                
                return response
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
@csrf_token_required
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
            # Create response
            response = jsonify({
                'message': 'Login successful',
                'user': {
                    'id': result['user']['id'],
                    'email': result['user']['email'],
                    'full_name': result['user']['full_name'],
                    'subscription_tier': result['user']['subscription_tier']
                }
                # Tokens no longer returned in response body
            })
            
            # Set httpOnly cookies for tokens
            max_age_access = 24 * 60 * 60  # 24 hours
            max_age_refresh = 30 * 24 * 60 * 60  # 30 days
            
            # Check if we're in production (use secure cookies only in production)
            is_production = os.getenv('RENDER_EXTERNAL_URL') is not None or 'onrender.com' in request.url_root
            
            response.set_cookie(
                'access_token',
                result['access_token'],
                max_age=max_age_access,
                httponly=True,
                secure=is_production,  # Only secure in production
                samesite='None' if is_production else 'Strict'  # None required for cross-origin in production
            )
            
            if result.get('refresh_token'):
                response.set_cookie(
                    'refresh_token',
                    result['refresh_token'],
                    max_age=max_age_refresh,
                    httponly=True,
                    secure=is_production,
                    samesite='None' if is_production else 'Strict'
                )
                
            return response, 200
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
        
        user = g.current_user
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
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
        
        # Check for Authorization header or cookie
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Verify token from Authorization header
                verify_jwt_in_request(locations=['headers'])
            except Exception:
                return jsonify({'error': 'Invalid token in header', 'valid': False}), 401
        else:
            try:
                # Verify token from cookie
                verify_jwt_in_request(locations=['cookies'])
            except Exception:
                return jsonify({'error': 'Invalid token in cookie', 'valid': False}), 401
        
        # Get user identity from verified token
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Invalid token payload', 'valid': False}), 401
        
        # Get user data
        user_data = supabase_service.get_user_by_id(user_id)
        if not user_data:
            return jsonify({'error': 'User not found', 'valid': False}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user_data['id'],
                'email': user_data['email'],
                'name': user_data['full_name'],
                'subscription_tier': user_data['subscription_tier']
            }
        }), 200
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Verify token error: {str(e)}")
        return jsonify({'error': 'Token verification failed', 'valid': False}), 500

@supabase_bp.route('/auth/refresh', methods=['POST'])
@supabase_auth_required
def refresh_token():
    """Refresh JWT token."""
    try:
        from flask_jwt_extended import create_access_token
        
        user = g.current_user
        
        # Create new access token using Flask-JWT-Extended
        new_access_token = create_access_token(
            identity=user['id'],
            additional_claims={
                'email': user['email'],
                'subscription_tier': user['subscription_tier']
            }
        )
        
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
        import logging
        logger = logging.getLogger(__name__)
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
@supabase_auth_required
def get_profile():
    """Get user profile."""
    try:
        user = g.current_user
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
        user = g.current_user
        
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
        
        logger.info(f"Attempting to upload profile image: {unique_filename}")
        
        try:
            # Read file content as bytes
            file.seek(0)  # Reset file pointer to beginning
            file_content = file.read()
            logger.info(f"File content read: {len(file_content)} bytes, type: {type(file_content)}")
            
            # Ensure we have bytes content
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            # Upload to Supabase Storage with correct parameters
            logger.info(f"Uploading to path: {unique_filename}")
            storage_response = supabase_service.client.storage.from_('profile-images').upload(
                file=file_content,
                path=unique_filename,
                file_options={'content-type': f'image/{file_extension}'}
            )
            
            logger.info(f"Storage response type: {type(storage_response)}, content: {storage_response}")
            
            # Check for errors in the response
            if hasattr(storage_response, 'error') and storage_response.error:
                logger.error(f"Supabase storage upload error: {storage_response.error}")
                return jsonify({'error': f'Failed to upload image to storage: {storage_response.error}'}), 500
            
            # Check if response is a dict with error
            if isinstance(storage_response, dict):
                if 'error' in storage_response and storage_response['error']:
                    logger.error(f"Supabase storage upload error: {storage_response['error']}")
                    return jsonify({'error': f'Failed to upload image to storage: {storage_response["error"]}'}), 500
                
                # Check for successful upload indicators
                if 'path' in storage_response or 'Key' in storage_response or 'fullPath' in storage_response:
                    logger.info("Upload appears successful based on response structure")
                else:
                    logger.warning(f"Unexpected response structure: {storage_response}")
            
            # Get public URL for the uploaded image
            try:
                public_url_response = supabase_service.client.storage.from_('profile-images').get_public_url(unique_filename)
                logger.info(f"Public URL response: {public_url_response}")
                
                # Handle different response formats
                image_url = None
                if isinstance(public_url_response, dict):
                    image_url = (public_url_response.get('publicUrl') or 
                               public_url_response.get('signedUrl') or 
                               public_url_response.get('url'))
                elif hasattr(public_url_response, 'publicUrl'):
                    image_url = public_url_response.publicUrl
                elif isinstance(public_url_response, str):
                    image_url = public_url_response
                else:
                    image_url = str(public_url_response) if public_url_response else None
                
                if not image_url:
                    logger.error(f"Failed to get public URL for uploaded image. Response: {public_url_response}")
                    return jsonify({'error': 'Failed to get image URL'}), 500
                    
            except Exception as url_error:
                logger.error(f"Error getting public URL: {url_error}")
                return jsonify({'error': 'Failed to get image URL'}), 500
            
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
        user = g.current_user
        
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
@supabase_auth_required
def get_usage_stats():
    """Get user usage statistics."""
    try:
        user = g.current_user
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
@supabase_auth_required
def get_usage_stats_alias():
    """Alias for get_usage_stats to support different frontend calls."""
    return get_usage_stats()

# API Key Management
@supabase_bp.route('/keys', methods=['GET'])
@supabase_auth_required
def list_api_keys():
    """List user's API keys."""
    try:
        user = g.current_user
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
        user = g.current_user
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

@supabase_bp.route('/keys/<key_id>', methods=['DELETE', 'OPTIONS'])
@supabase_auth_required
def delete_api_key(key_id):
    """Delete an API key."""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        origin = request.headers.get('Origin')
        if origin in ["https://censorly.vercel.app", "http://localhost:3000", "http://localhost:5173"]:
            response.headers.add("Access-Control-Allow-Origin", origin)
            response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-API-Key,X-Requested-With,Accept,Origin")
        response.headers.add('Access-Control-Allow-Methods', "DELETE,OPTIONS")
        return response

    # Get authenticated user
    user = g.current_user
    
    try:
        result = supabase_service.delete_api_key(key_id, user['id'])
        
        if result['success']:
            import logging
            logger = logging.getLogger(__name__)
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
        user = g.current_user
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
@secure_api_key_required  # Use our enhanced secure API key decorator
def create_job():
    """Create a new job via API with enhanced security."""
    try:
        user = g.current_user
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
        user = g.current_user
        job = supabase_service.get_job(job_id, user['id'])
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job}), 200
        
    except Exception as e:
        logger.error(f"Get job error: {str(e)}")
        return jsonify({'error': 'Failed to get job'}), 500

# ===== VIDEO PROCESSING ENDPOINTS =====

@supabase_bp.route('/process-video', methods=['POST'])
@csrf_protect
@supabase_auth_required
def process_video():
    """
    Main video processing endpoint.
    Handles video upload and initiates processing job.
    """
    try:
        user = g.current_user
        
        # Check if file is present
        file_param = 'video_file'  # Use consistent parameter name
        if file_param not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files[file_param]
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Import security utils
        from utils.security_utils import validate_video_file, is_allowed_extension, get_secure_filename
        
        # Validate file type by extension first
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm'}
        if not is_allowed_extension(file.filename, allowed_extensions):
            return jsonify({'error': 'Unsupported file format. Supported: MP4, AVI, MOV, MKV, WMV, WEBM'}), 400
            
        # Validate file content using magic numbers
        if not validate_video_file(file):
            return jsonify({'error': 'Invalid video file. The file content does not match a valid video format.'}), 400
        
        # Check file size (500MB limit)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = 500 * 1024 * 1024  # 500MB
        if file_size > max_size:
            return jsonify({'error': 'File size exceeds 500MB limit'}), 400
        
        # Get processing parameters
        censoring_mode = request.form.get('censoring_mode', 'beep')
        profanity_threshold = float(request.form.get('profanity_threshold', 0.8))
        languages = json.loads(request.form.get('languages', '["en"]'))
        
        # Validate parameters
        if censoring_mode not in ['beep', 'mute', 'cut']:
            return jsonify({'error': 'Invalid censoring mode. Must be: beep, mute, or cut'}), 400
        
        if not 0.0 <= profanity_threshold <= 1.0:
            return jsonify({'error': 'Profanity threshold must be between 0.0 and 1.0'}), 400
        
        # Check subscription limits
        plan_limits = supabase_service.get_plan_limits(user['subscription_tier'])
        
        # Check monthly processing limit
        if plan_limits['monthly_limit'] > 0:
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_jobs = supabase_service.client.table("jobs").select("id")\
                .eq("user_id", user['id'])\
                .gte("created_at", current_month_start.isoformat())\
                .execute()
            
            if len(monthly_jobs.data or []) >= plan_limits['monthly_limit']:
                return jsonify({'error': 'Monthly processing limit reached'}), 429
        
        # Create upload directory
        upload_dir = Path(f"uploads/{user['id']}")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file with secure name
        from utils.security_utils import get_secure_filename, compute_file_hash
        
        # Generate secure filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        secure_name = get_secure_filename(file.filename)
        safe_filename = f"{timestamp}_{secure_name}"
        file_path = upload_dir / safe_filename
        
        # Compute file hash for integrity verification
        file_hash = compute_file_hash(file)
        
        file.save(str(file_path))
        
        # Create processing job
        job_data = {
            'original_filename': file.filename,  # Original filename from request
            'stored_filename': safe_filename,
            'file_path': str(file_path),
            'file_size': file_size,
            'censoring_mode': censoring_mode,
            'profanity_threshold': profanity_threshold,
            'languages': json.dumps(languages),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase_service.create_job(user['id'], job_data)
        
        if not result['success']:
            # Clean up uploaded file on failure
            if file_path.exists():
                file_path.unlink()
            return jsonify({'error': result['error']}), 500
        
        job_id = result['job']['id']
        
        # TODO: Queue background processing task
        # For now, return job_id for polling
        
        logger.info(f"Video upload successful. Job ID: {job_id}, User: {user['email']}")
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'job_id': job_id,
            'status': 'pending',
            'estimated_processing_time': '2-5 minutes'
        }), 202
        
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        return jsonify({'error': 'Video processing failed'}), 500

@supabase_bp.route('/jobs/<job_id>/status', methods=['GET'])
@supabase_auth_required
def get_job_status(job_id):
    """Get detailed job status and progress."""
    try:
        user = g.current_user
        job = supabase_service.get_job(job_id, user['id'])
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({
            'job_id': job['id'],
            'status': job['status'],
            'progress': job.get('progress', 0),
            'created_at': job['created_at'],
            'updated_at': job.get('updated_at'),
            'error_message': job.get('error_message'),
            'result': job.get('result')
        }), 200
        
    except Exception as e:
        logger.error(f"Get job status error: {str(e)}")
        return jsonify({'error': 'Failed to get job status'}), 500

@supabase_bp.route('/download/<job_id>', methods=['GET'])
@supabase_auth_required
def download_processed_video(job_id):
    """Download processed video file."""
    try:
        user = g.current_user
        job = supabase_service.get_job(job_id, user['id'])
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job['status'] != 'completed':
            return jsonify({'error': 'Job not completed yet'}), 400
        
        # Check if processed file exists
        result = job.get('result', {})
        processed_file_path = result.get('processed_file_path')
        
        if not processed_file_path or not os.path.exists(processed_file_path):
            return jsonify({'error': 'Processed file not found'}), 404
        
        # Return file for download
        return send_file(
            processed_file_path,
            as_attachment=True,
            download_name=f"processed_{job['original_filename']}"
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

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
