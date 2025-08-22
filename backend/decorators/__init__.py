# Decorators module for authentication and security
try:
    from .api_security import secure_api_key_required
except ImportError:
    # If the module is not available, provide a fallback
    def secure_api_key_required(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
