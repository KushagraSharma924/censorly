"""
Rate Limiting Decorators for Flask API Endpoints
Provides decorators to apply rate limiting to API routes.
"""

from functools import wraps
from flask import request, jsonify, g
from backend.services.rate_limiter import check_api_rate_limit, get_rate_limit_headers, rate_limiter
from backend.models.saas_models import APIKey

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
            
            # Check rate limit
            is_allowed, result = check_api_rate_limit(api_key, endpoint_type)
            
            if not is_allowed:
                error_response = jsonify(result)
                error_response.status_code = 429  # Too Many Requests
                if 'retry_after' in result:
                    error_response.headers['Retry-After'] = str(result['retry_after'])
                return error_response
            
            # Store API key info in Flask's g object for use in the endpoint
            g.api_key_id = result['api_key_id']
            g.user_id = result['user_id']
            g.rate_limit_info = result['rate_limit_info']
            
            # Call the actual endpoint function
            response = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if hasattr(g, 'api_key_id'):
                api_key_obj = APIKey.query.get(g.api_key_id)
                if api_key_obj:
                    headers = get_rate_limit_headers(api_key_obj)
                    if hasattr(response, 'headers'):
                        response.headers.update(headers)
                    elif isinstance(response, tuple) and len(response) >= 2:
                        # Handle tuple responses (response, status_code, headers)
                        if len(response) == 3:
                            response[2].update(headers)
                        else:
                            response = (response[0], response[1], headers)
            
            return response
        
        return decorated_function
    return decorator

def rate_limit_only(endpoint_type='general'):
    """
    Decorator that only applies rate limiting without requiring API key.
    Uses IP-based rate limiting for endpoints that don't require authentication.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For non-API endpoints, implement IP-based rate limiting
            client_ip = request.remote_addr
            
            # Simple IP-based rate limiting (in production, use Redis)
            if not hasattr(rate_limit_only, '_ip_requests'):
                rate_limit_only._ip_requests = {}
            
            import time
            now = time.time()
            minute_ago = now - 60
            
            # Clean old entries
            if client_ip in rate_limit_only._ip_requests:
                rate_limit_only._ip_requests[client_ip] = [
                    req_time for req_time in rate_limit_only._ip_requests[client_ip] 
                    if req_time > minute_ago
                ]
            else:
                rate_limit_only._ip_requests[client_ip] = []
            
            # Check limit (10 requests per minute for IP-based)
            if len(rate_limit_only._ip_requests[client_ip]) >= 10:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests from this IP address',
                    'retry_after': 60
                }), 429
            
            # Record this request
            rate_limit_only._ip_requests[client_ip].append(now)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_api_usage_stats():
    """
    Get API usage statistics for the current request's API key.
    Call this from within an endpoint decorated with @require_api_key_with_rate_limit
    """
    if hasattr(g, 'api_key_id'):
        api_key_obj = APIKey.query.get(g.api_key_id)
        if api_key_obj:
            return rate_limiter.get_usage_stats(api_key_obj)
    return None
