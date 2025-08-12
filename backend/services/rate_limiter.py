"""
Rate Limiting Service
Implements rate limiting based on user ID and subscription tiers.
Previously used API keys for tracking, but now uses user_id to prevent bypassing
rate limits by creating multiple API keys.
"""

from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading

# Import models (will be set by app context)
db = None
APIKey = None
User = None

def init_rate_limiter(app_db, app_apikey, app_user):
    """Initialize rate limiter with app models."""
    global db, APIKey, User
    db = app_db
    APIKey = app_apikey  
    User = app_user

class RateLimiter:
    """Rate limiter for API keys with tier-based limits."""
    
    def __init__(self):
        # In-memory storage for rate limiting (in production, use Redis)
        self._requests = defaultdict(list)
        self._lock = threading.Lock()
        
        # Rate limits per tier (requests per minute)
        self.TIER_LIMITS = {
            'free': {
                'general': {
                    'requests_per_minute': 5,
                    'requests_per_hour': 100,
                    'requests_per_day': 1000
                },
                'processing': {
                    'requests_per_minute': 1,
                    'requests_per_hour': 10,
                    'requests_per_day': 10
                },
                'upload': {
                    'requests_per_minute': 1,
                    'requests_per_hour': 5,
                    'requests_per_day': 10
                }
            },
            'basic': {
                'general': {
                    'requests_per_minute': 20,
                    'requests_per_hour': 500,
                    'requests_per_day': 5000
                },
                'processing': {
                    'requests_per_minute': 5,
                    'requests_per_hour': 100,
                    'requests_per_day': 1000
                },
                'upload': {
                    'requests_per_minute': 5,
                    'requests_per_hour': 50,
                    'requests_per_day': 100
                }
            },
            'pro': {
                'general': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 2000,
                    'requests_per_day': 20000
                },
                'processing': {
                    'requests_per_minute': 20,
                    'requests_per_hour': 500,
                    'requests_per_day': 5000
                },
                'upload': {
                    'requests_per_minute': 20,
                    'requests_per_hour': 200,
                    'requests_per_day': 500
                }
            },
            'enterprise': {
                'general': {
                    'requests_per_minute': 500,
                    'requests_per_hour': 10000,
                    'requests_per_day': 100000
                },
                'processing': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 2000,
                    'requests_per_day': 20000
                },
                'upload': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 1000,
                    'requests_per_day': 2000
                }
            }
        }
    
    def check_rate(self, user_id, endpoint_type='general', tier='free'):
        """
        Check if a request is allowed based on rate limits.
        
        Args:
            user_id: User identifier (not API key, to prevent multi-key bypass)
            endpoint_type: Type of endpoint being accessed
            tier: Subscription tier
            
        Returns:
            bool: True if allowed, False if rate limited
        """
        
        if not api_key_obj or not api_key_obj.is_active:
            return False, 0, 0, "Invalid or inactive API key"
        
        # Get user's subscription tier
        user = User.query.get(api_key_obj.user_id)
        if not user:
            return False, 0, 0, "User not found"
        
        tier = user.subscription_tier
        tier_limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['free'])
        limits = tier_limits.get(endpoint_type, tier_limits.get('general', tier_limits['general']))
        
        with self._lock:
            key_id = api_key_obj.id
            now = time.time()
            
            # Clean old entries (older than 24 hours)
            cutoff_time = now - 86400  # 24 hours
            self._requests[key_id] = [req_time for req_time in self._requests[key_id] if req_time > cutoff_time]
            
            # Check limits
            minute_ago = now - 60
            hour_ago = now - 3600
            day_ago = now - 86400
            
            requests_last_minute = len([t for t in self._requests[key_id] if t > minute_ago])
            requests_last_hour = len([t for t in self._requests[key_id] if t > hour_ago])
            requests_last_day = len([t for t in self._requests[key_id] if t > day_ago])
            
            # Check each limit
            if requests_last_minute >= limits['requests_per_minute']:
                retry_after = 60 - (now - max([t for t in self._requests[key_id] if t > minute_ago], default=now))
                return False, max(1, int(retry_after)), requests_last_minute, f"Rate limit exceeded: {requests_last_minute}/{limits['requests_per_minute']} requests per minute"
            
            if requests_last_hour >= limits['requests_per_hour']:
                retry_after = 3600 - (now - max([t for t in self._requests[key_id] if t > hour_ago], default=now))
                return False, max(1, int(retry_after)), requests_last_hour, f"Rate limit exceeded: {requests_last_hour}/{limits['requests_per_hour']} requests per hour"
            
            if requests_last_day >= limits['requests_per_day']:
                retry_after = 86400 - (now - max([t for t in self._requests[key_id] if t > day_ago], default=now))
                return False, max(1, int(retry_after)), requests_last_day, f"Rate limit exceeded: {requests_last_day}/{limits['requests_per_day']} requests per day"
            
            # Record this request
            self._requests[key_id].append(now)
            
            # Update API key usage
            api_key_obj.usage_count += 1
            api_key_obj.last_used = datetime.utcnow()
            db.session.commit()
            
            limit_info = {
                'tier': tier,
                'limits': limits,
                'current_usage': {
                    'minute': requests_last_minute + 1,
                    'hour': requests_last_hour + 1,
                    'day': requests_last_day + 1
                }
            }
            
            return True, 0, requests_last_minute + 1, limit_info
    
    def get_usage_stats(self, api_key_obj, endpoint_type='general'):
        """Get current usage statistics for an API key."""
        if not api_key_obj:
            return None
        
        user = User.query.get(api_key_obj.user_id)
        if not user:
            return None
        
        tier = user.subscription_tier
        tier_limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['free'])
        limits = tier_limits.get(endpoint_type, tier_limits.get('general', tier_limits['general']))
        
        with self._lock:
            key_id = api_key_obj.id
            now = time.time()
            
            minute_ago = now - 60
            hour_ago = now - 3600
            day_ago = now - 86400
            
            requests_last_minute = len([t for t in self._requests[key_id] if t > minute_ago])
            requests_last_hour = len([t for t in self._requests[key_id] if t > hour_ago])
            requests_last_day = len([t for t in self._requests[key_id] if t > day_ago])
            
            return {
                'tier': tier,
                'endpoint_type': endpoint_type,
                'limits': limits,
                'current_usage': {
                    'minute': requests_last_minute,
                    'hour': requests_last_hour,
                    'day': requests_last_day
                },
                'remaining': {
                    'minute': max(0, limits['requests_per_minute'] - requests_last_minute),
                    'hour': max(0, limits['requests_per_hour'] - requests_last_hour),
                    'day': max(0, limits['requests_per_day'] - requests_last_day)
                }
            }
    
    def reset_rate_limit(self, api_key_obj):
        """Reset rate limit for an API key (admin function)."""
        if api_key_obj:
            with self._lock:
                self._requests[api_key_obj.id] = []
                return True
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_api_rate_limit(api_key_string, endpoint_type='general'):
    """
    Decorator function to check rate limits for API endpoints.
    
    Args:
        api_key_string: The raw API key string
        endpoint_type: Type of endpoint being accessed
        
    Returns:
        tuple: (is_allowed, error_response)
    """
    
    if not api_key_string:
        return False, {
            'error': 'API key required',
            'code': 'MISSING_API_KEY'
        }
    
    # Verify and get API key object
    api_key_obj = APIKey.verify_key(api_key_string)
    if not api_key_obj:
        return False, {
            'error': 'Invalid API key',
            'code': 'INVALID_API_KEY'
        }
    
    # Check rate limit
    is_allowed, retry_after, current_usage, limit_info = rate_limiter.check_rate_limit(
        api_key_obj, endpoint_type
    )
    
    if not is_allowed:
        return False, {
            'error': 'Rate limit exceeded',
            'code': 'RATE_LIMIT_EXCEEDED',
            'message': limit_info,
            'retry_after': retry_after,
            'current_usage': current_usage
        }
    
    return True, {
        'api_key_id': api_key_obj.id,
        'user_id': str(api_key_obj.user_id),
        'rate_limit_info': limit_info
    }

def get_rate_limit_headers(api_key_obj):
    """Get rate limit headers for API responses."""
    if not api_key_obj:
        return {}
    
    stats = rate_limiter.get_usage_stats(api_key_obj)
    if not stats:
        return {}
    
    return {
        'X-RateLimit-Limit-Minute': str(stats['limits']['requests_per_minute']),
        'X-RateLimit-Limit-Hour': str(stats['limits']['requests_per_hour']),
        'X-RateLimit-Limit-Day': str(stats['limits']['requests_per_day']),
        'X-RateLimit-Remaining-Minute': str(stats['remaining']['minute']),
        'X-RateLimit-Remaining-Hour': str(stats['remaining']['hour']),
        'X-RateLimit-Remaining-Day': str(stats['remaining']['day']),
        'X-RateLimit-Tier': stats['tier']
    }
