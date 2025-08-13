"""
Rate Limiting Decorators for Flask API Endpoints - Supabase Production Version
Provides decorators to apply rate limiting to API routes using Supabase.
"""

from functools import wraps
from flask import request, jsonify, g, current_app
import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# In-memory rate limiting store (in production, use Redis)
rate_limit_store = {}

def get_rate_limits_for_tier(tier: str) -> Dict[str, int]:
    """Get rate limits based on subscription tier."""
    limits = {
        'free': {
            'requests_per_minute': 10,
            'requests_per_hour': 100,
            'upload_per_hour': 5,
            'processing_per_hour': 5
        },
        'basic': {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'upload_per_hour': 50,
            'processing_per_hour': 50
        },
        'premium': {
            'requests_per_minute': 200,
            'requests_per_hour': 5000,
            'upload_per_hour': 200,
            'processing_per_hour': 200
        },
        'enterprise': {
            'requests_per_minute': 1000,
            'requests_per_hour': 20000,
            'upload_per_hour': 1000,
            'processing_per_hour': 1000
        }
    }
    return limits.get(tier, limits['free'])

def check_rate_limit(identifier: str, endpoint_type: str, limits: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if request is within rate limits.
    
    Args:
        identifier: Unique identifier (API key or IP)
        endpoint_type: Type of endpoint ('general', 'upload', 'processing')
        limits: Rate limit configuration
    
    Returns:
        Tuple of (is_allowed, response_data)
    """
    now = time.time()
    minute_ago = now - 60
    hour_ago = now - 3600
    
    # Initialize tracking for this identifier
    if identifier not in rate_limit_store:
        rate_limit_store[identifier] = {
            'requests': [],
            'uploads': [],
            'processing': []
        }
    
    store = rate_limit_store[identifier]
    
    # Clean old entries
    store['requests'] = [t for t in store['requests'] if t > minute_ago]
    store['uploads'] = [t for t in store['uploads'] if t > hour_ago]
    store['processing'] = [t for t in store['processing'] if t > hour_ago]
    
    # Determine which limit to check
    if endpoint_type == 'upload':
        current_count = len(store['uploads'])
        limit_key = 'upload_per_hour'
        time_window = 3600
        window_name = 'hour'
    elif endpoint_type == 'processing':
        current_count = len(store['processing'])
        limit_key = 'processing_per_hour'
        time_window = 3600
        window_name = 'hour'
    else:
        current_count = len(store['requests'])
        limit_key = 'requests_per_minute'
        time_window = 60
        window_name = 'minute'
    
    limit = limits.get(limit_key, 10)
    
    if current_count >= limit:
        return False, {
            'error': 'Rate limit exceeded',
            'message': f'Too many {endpoint_type} requests. Limit: {limit} per {window_name}',
            'retry_after': time_window,
            'current_usage': current_count,
            'limit': limit,
            'window': window_name
        }
    
    # Record this request
    if endpoint_type == 'upload':
        store['uploads'].append(now)
    elif endpoint_type == 'processing':
        store['processing'].append(now)
    else:
        store['requests'].append(now)
    
    return True, {
        'current_usage': current_count + 1,
        'limit': limit,
        'window': window_name,
        'remaining': limit - current_count - 1
    }

def get_user_from_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Get user information from API key using Supabase."""
    try:
        from services.supabase_service import supabase_service
        
        # Query api_keys table
        response = supabase_service.client.table('api_keys').select(
            'id, user_id, name, is_active, created_at, users(subscription_tier, email)'
        ).eq('key_hash', api_key).eq('is_active', True).execute()
        
        if response.data:
            api_key_data = response.data[0]
            user_data = api_key_data.get('users', {})
            
            return {
                'api_key_id': api_key_data['id'],
                'user_id': api_key_data['user_id'],
                'subscription_tier': user_data.get('subscription_tier', 'free'),
                'api_key_name': api_key_data['name']
            }
        
        return None
    except Exception as e:
        logger.error(f"Error getting user from API key: {e}")
        return None

def require_api_key_with_rate_limit(endpoint_type='general'):
    """
    Decorator that requires API key authentication with rate limiting.
    
    Args:
        endpoint_type: Type of endpoint ('general', 'upload', 'processing')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not api_key:
                return jsonify({
                    'error': 'API key required',
                    'message': 'Please provide an API key in X-API-Key header or Authorization header'
                }), 401
            
            # Get user info from API key
            user_info = get_user_from_api_key(api_key)
            if not user_info:
                return jsonify({
                    'error': 'Invalid API key',
                    'message': 'The provided API key is invalid or inactive'
                }), 401
            
            # Get rate limits for user's tier
            limits = get_rate_limits_for_tier(user_info['subscription_tier'])
            
            # Check rate limit
            is_allowed, result = check_rate_limit(api_key, endpoint_type, limits)
            
            if not is_allowed:
                error_response = jsonify(result)
                error_response.status_code = 429  # Too Many Requests
                if 'retry_after' in result:
                    error_response.headers['Retry-After'] = str(result['retry_after'])
                    error_response.headers['X-RateLimit-Limit'] = str(result['limit'])
                    error_response.headers['X-RateLimit-Remaining'] = '0'
                    error_response.headers['X-RateLimit-Reset'] = str(int(time.time() + result['retry_after']))
                return error_response
            
            # Store API key info in Flask's g object for use in the endpoint
            g.api_key_id = user_info['api_key_id']
            g.user_id = user_info['user_id']
            g.subscription_tier = user_info['subscription_tier']
            g.rate_limit_info = result
            
            # Call the actual endpoint function
            response = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if isinstance(response, tuple):
                response_data, status_code = response[0], response[1]
                headers = response[2] if len(response) > 2 else {}
            else:
                response_data = response
                status_code = 200
                headers = {}
            
            # Add rate limiting headers
            headers.update({
                'X-RateLimit-Limit': str(result['limit']),
                'X-RateLimit-Remaining': str(result['remaining']),
                'X-RateLimit-Window': result['window']
            })
            
            if isinstance(response, tuple):
                return response_data, status_code, headers
            else:
                # For Response objects, add headers
                if hasattr(response, 'headers'):
                    response.headers.update(headers)
                return response
        
        return decorated_function
    return decorator

def rate_limit_only(endpoint_type='general', per_minute=60, burst_limit=10):
    """
    Decorator that only applies rate limiting without requiring API key.
    Uses IP-based rate limiting for endpoints that don't require authentication.
    
    Args:
        endpoint_type: Type of endpoint
        per_minute: Requests allowed per minute
        burst_limit: Burst requests allowed
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as identifier for rate limiting
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            if ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            # Create limits for IP-based rate limiting
            limits = {
                'requests_per_minute': per_minute,
                'upload_per_hour': burst_limit,
                'processing_per_hour': burst_limit
            }
            
            # Check rate limit using IP-based identifier
            is_allowed, result = check_rate_limit(
                f"ip_{client_ip}", 
                endpoint_type, 
                limits
            )
            
            if not is_allowed:
                error_response = jsonify(result)
                error_response.status_code = 429  # Too Many Requests
                if 'retry_after' in result:
                    error_response.headers['Retry-After'] = str(result['retry_after'])
                    error_response.headers['X-RateLimit-Limit'] = str(result['limit'])
                    error_response.headers['X-RateLimit-Remaining'] = '0'
                    error_response.headers['X-RateLimit-Reset'] = str(int(time.time() + result['retry_after']))
                return error_response
            
            # Store rate limit info in Flask's g object
            g.rate_limit_info = result
            g.client_ip = client_ip
            
            # Call the actual endpoint function
            response = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if isinstance(response, tuple):
                response_data, status_code = response[0], response[1]
                headers = response[2] if len(response) > 2 else {}
            else:
                response_data = response
                status_code = 200
                headers = {}
            
            # Add rate limiting headers
            headers.update({
                'X-RateLimit-Limit': str(result['limit']),
                'X-RateLimit-Remaining': str(result['remaining']),
                'X-RateLimit-Window': result['window']
            })
            
            if isinstance(response, tuple):
                return response_data, status_code, headers
            else:
                # For Response objects, add headers
                if hasattr(response, 'headers'):
                    response.headers.update(headers)
                return response
        
        return decorated_function
    return decorator

def cleanup_rate_limit_store():
    """Clean up old entries from the rate limit store."""
    now = time.time()
    hour_ago = now - 3600
    
    for identifier in list(rate_limit_store.keys()):
        store = rate_limit_store[identifier]
        store['requests'] = [t for t in store['requests'] if t > now - 60]
        store['uploads'] = [t for t in store['uploads'] if t > hour_ago]
        store['processing'] = [t for t in store['processing'] if t > hour_ago]
        
        # Remove empty entries
        if not any([store['requests'], store['uploads'], store['processing']]):
            del rate_limit_store[identifier]

# Clean up every 10 minutes
import threading
import atexit

def periodic_cleanup():
    cleanup_rate_limit_store()
    threading.Timer(600.0, periodic_cleanup).start()

# Start cleanup thread
periodic_cleanup()

# Ensure cleanup on exit
atexit.register(cleanup_rate_limit_store)
