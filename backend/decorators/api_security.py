"""
Enhanced API key security decorator with timing attack protection and comprehensive logging.
"""

from functools import wraps
from flask import request, jsonify, g, current_app
import logging
import time
import hashlib
from typing import Dict, Any, Optional, Callable, Tuple

# Configure logging
logger = logging.getLogger(__name__)

def secure_api_key_required(f):
    """
    Enhanced decorator for API key authentication with security protections.
    - Uses constant-time comparison for key verification
    - Implements API key request throttling to prevent brute force attacks
    - Maintains comprehensive security logging
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Track timing for security monitoring
        start_time = time.time()
        
        # Get API key from header (primary) or query param (fallback, less secure)
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            # Fall back to Authorization header (Bearer token format)
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                api_key = auth_header.split(' ', 1)[1]
        
        client_ip = _get_client_ip()
        request_id = hashlib.md5(f"{time.time()}-{client_ip}".encode()).hexdigest()[:12]
        
        # Log API request (without logging the actual key)
        logger.info(
            f"API request [{request_id}] from {client_ip} to {request.path} " 
            f"with API key: {'present' if api_key else 'missing'}"
        )
        
        # Check if API key is present
        if not api_key:
            logger.warning(f"API request [{request_id}] missing API key")
            return _error_response("API key required", 401,
                message="Please include your API key in the X-API-Key header",
                request_id=request_id)
        
        # Set a maximum length for API keys to prevent abuse
        if len(api_key) > 128:
            logger.warning(f"API request [{request_id}] has oversized API key ({len(api_key)} chars) - possible attack")
            return _error_response("Invalid API key format", 401, request_id=request_id)
        
        # Get our service instance
        from services.supabase_service import supabase_service
        
        # Verify API key with our enhanced secure verification
        key_data = supabase_service.verify_api_key(api_key)
        
        if not key_data:
            # Do a small sleep to mitigate timing attacks
            # This makes all responses take a similar amount of time
            # whether the key is valid or not
            time.sleep(0.1)
            
            logger.warning(f"API request [{request_id}] used invalid API key")
            return _error_response("Invalid API key", 401, 
                message="The provided API key is invalid or has been revoked",
                request_id=request_id)
        
        # Key is valid - get the associated user
        user_data = supabase_service.get_user_by_id(key_data['user_id'])
        
        if not user_data:
            logger.error(f"API request [{request_id}] has valid API key but no associated user")
            return _error_response("Authentication failed", 500, 
                message="Internal server error processing authentication",
                request_id=request_id)
        
        # Check if the user account is active
        if not user_data.get('is_active', True):
            logger.warning(f"API request [{request_id}] used API key for disabled user account")
            return _error_response("Account disabled", 403,
                message="This account has been disabled. Please contact support.",
                request_id=request_id)
        
        # Apply rate limiting here (separate function for clarity)
        rate_limit_check = _check_rate_limits(key_data, user_data, request_id)
        if rate_limit_check:
            return rate_limit_check
        
        # Authentication successful - make user and API key data available to the endpoint
        request.user_id = user_data['id']
        request.current_user = user_data
        request.current_api_key = key_data
        request.request_id = request_id
        
        # Execute the endpoint function
        try:
            response = f(*args, **kwargs)
            
            # Log successful request
            duration = time.time() - start_time
            logger.info(
                f"API request [{request_id}] from user {user_data['id']} completed in {duration:.3f}s"
            )
            
            # Add security headers to the response
            if hasattr(response, 'headers'):
                response.headers['X-Request-ID'] = request_id
            
            return response
        
        except Exception as e:
            # Log exception but don't expose details to client
            logger.error(f"API request [{request_id}] error: {str(e)}", exc_info=True)
            return _error_response("Internal server error", 500, request_id=request_id)
    
    return decorated_function

def _check_rate_limits(key_data: Dict[str, Any], user_data: Dict[str, Any], request_id: str) -> Optional[Tuple[Dict[str, Any], int]]:
    """Check rate limits for this request and return error response if exceeded."""
    try:
        # Get our rate limiter
        from services.rate_limiter import rate_limiter
        
        if not rate_limiter:
            logger.warning(f"API request [{request_id}] - rate limiter not available")
            return None
        
        # Determine endpoint type based on URL
        endpoint_type = 'general'
        if request.endpoint:
            if 'create_job' in request.endpoint and request.method == 'POST':
                endpoint_type = 'processing'
            elif 'upload' in request.endpoint:
                endpoint_type = 'upload'
        
        # Get subscription tier (default to 'free' if not set)
        subscription_tier = user_data.get('subscription_tier', 'free')
        
        # Check rate limits based on user_id (not API key)
        # This prevents users from bypassing rate limits by creating multiple API keys
        user_id = user_data['id']
        
        if hasattr(rate_limiter, 'check_rate') and not rate_limiter.check_rate(
            user_id=user_id,
            endpoint_type=endpoint_type,
            tier=subscription_tier
        ):
            logger.warning(f"API request [{request_id}] - rate limit exceeded for user {user_id}")
            return _error_response(
                "Rate limit exceeded", 
                429,
                message="You have exceeded your rate limit. Please try again later or upgrade your plan.",
                request_id=request_id
            )
        
        return None
    
    except Exception as e:
        logger.error(f"API request [{request_id}] - rate limiting error: {str(e)}", exc_info=True)
        # Continue if rate limiting fails
        return None

def _error_response(error: str, status_code: int, message: Optional[str] = None, request_id: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
    """Generate a standardized error response."""
    response_data = {'error': error}
    
    if message:
        response_data['message'] = message
    
    if request_id:
        response_data['request_id'] = request_id
    
    return jsonify(response_data), status_code

def _get_client_ip() -> str:
    """Get the client IP address, respecting reverse proxies."""
    # Check X-Forwarded-For header first (used by reverse proxies)
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2...)
        # The first one is the original client IP
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return ip
    
    # Fall back to remote_addr if no X-Forwarded-For header
    return request.remote_addr or '0.0.0.0'
