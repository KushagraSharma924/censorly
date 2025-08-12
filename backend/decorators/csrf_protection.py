"""
CSRF Protection for API endpoints
"""

from flask import Blueprint, request, jsonify, session, current_app
from functools import wraps
import secrets
import logging
import time

logger = logging.getLogger(__name__)

def generate_csrf_token():
    """
    Generate a new CSRF token.
    
    Returns:
        str: A secure random token
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    
    return session['csrf_token']

def csrf_protect(f):
    """
    Decorator to require CSRF token for state-changing operations.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF check for GET, HEAD, OPTIONS, TRACE
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return f(*args, **kwargs)
            
        # For state-changing methods (POST, PUT, DELETE, etc.)
        # Check for token in multiple possible locations
        
        # 1. Check for X-CSRF-TOKEN header
        token = request.headers.get('X-CSRF-TOKEN')
        
        # 2. Check for X-XSRF-TOKEN header (alternate name)
        if not token:
            token = request.headers.get('X-XSRF-TOKEN')
            
        # 3. Check for token in form data
        if not token and request.form:
            token = request.form.get('csrf_token')
            
        # 4. Check for token in JSON body
        if not token and request.is_json:
            json_data = request.get_json(silent=True) or {}
            token = json_data.get('csrf_token')
            
        # Validate token
        expected_token = session.get('csrf_token')
        
        if not expected_token:
            logger.warning("CSRF validation failed: No token in session")
            return jsonify({
                'error': 'CSRF token missing from session',
                'code': 'CSRF_SESSION_ERROR'
            }), 400
            
        if not token:
            logger.warning("CSRF validation failed: No token in request")
            return jsonify({
                'error': 'CSRF token required',
                'code': 'CSRF_REQUIRED'
            }), 403
            
        # Constant time comparison to prevent timing attacks
        if not secrets.compare_digest(token, expected_token):
            logger.warning("CSRF validation failed: Token mismatch")
            return jsonify({
                'error': 'Invalid CSRF token',
                'code': 'CSRF_INVALID'
            }), 403
            
        return f(*args, **kwargs)
        
    return decorated_function

def csrf_token_required(f):
    """
    Decorator that adds CSRF token to the response context.
    Use with template rendering to insert tokens into forms.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = generate_csrf_token()
        response = f(*args, **kwargs)
        
        # If response is a tuple (response, status_code)
        if isinstance(response, tuple):
            response_obj = response[0]
            # If the response is JSON, add the CSRF token
            if hasattr(response_obj, 'set_cookie'):
                response_obj.set_cookie(
                    'XSRF-TOKEN',
                    token,
                    httponly=False,  # Frontend needs to read it
                    samesite='Strict',
                    secure=not current_app.debug
                )
        
        return response
        
    return decorated_function
