"""
Supabase Database Service for AI Profanity Filter SaaS Platform
Complete replacement for SQLAlchemy with pure Supabase operations.
"""

import os
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import uuid
import secrets
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    Client = None

logger = logging.getLogger(__name__)

class SupabaseService:
    """Complete database service using Supabase."""
    
    def __init__(self):
        """Initialize Supabase service."""
        if not HAS_SUPABASE:
            raise Exception("Supabase client library not installed. Run: pip install supabase")
        
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_anon_key = os.environ.get('SUPABASE_KEY')  # For auth operations
        self.supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')  # For admin operations
        
        if not self.supabase_url or not self.supabase_service_key:
            raise Exception("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
        
        # Use service key for database operations (bypasses RLS)
        self.client = create_client(self.supabase_url, self.supabase_service_key)
        logger.info("Supabase service initialized with service key")
        
        # Ensure storage buckets exist
        self.ensure_storage_buckets()
    
    # User Management
    def create_user(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Create a new user with simple password storage (no Supabase Auth)."""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return {"success": False, "error": "User already exists"}
            
            # Create user data
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "full_name": full_name,
                "password_hash": generate_password_hash(password),
                "subscription_tier": "free",
                "is_active": True,
                "is_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert user into database
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                logger.info(f"User created successfully: {email}")
                return {
                    "success": True,
                    "user": result.data[0]
                }
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with password verification (no Supabase Auth)."""
        try:
            # Get user from database
            user_data = self.get_user_by_email(email)
            
            if not user_data:
                return {"success": False, "error": "Invalid credentials"}
            
            # Check if user is active
            if not user_data.get('is_active', True):
                return {"success": False, "error": "Account is deactivated"}
            
            # Verify password
            if not check_password_hash(user_data['password_hash'], password):
                return {"success": False, "error": "Invalid credentials"}
            
            # Generate JWT tokens first for faster response
            from flask_jwt_extended import create_access_token, create_refresh_token
            
            access_token = create_access_token(
                identity=user_data['id'],
                additional_claims={
                    'email': user_data['email'],
                    'subscription_tier': user_data['subscription_tier']
                }
            )
            
            refresh_token = create_refresh_token(identity=user_data['id'])
            
            # Update last login asynchronously (non-blocking)
            try:
                self.client.table("users").update({
                    "last_login": datetime.utcnow().isoformat()
                }).eq("id", user_data['id']).execute()
            except Exception as login_update_error:
                # Don't fail login if last_login update fails
                logger.warning(f"Failed to update last_login: {login_update_error}")
            
            return {
                "success": True,
                "user": user_data,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {"success": False, "error": "Authentication failed"}
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Get user by email error: {str(e)}")
            return None
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data."""
        try:
            result = self.client.table("users").update(data).eq("id", user_id).execute()
            return {
                "success": True,
                "user": result.data[0] if result.data else None
            }
        except Exception as e:
            logger.error(f"Update user error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Job Management
    def create_job(self, user_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job."""
        try:
            job_data['user_id'] = user_id
            job_data['id'] = str(uuid.uuid4())
            
            result = self.client.table("jobs").insert(job_data).execute()
            return {
                "success": True,
                "job": result.data[0] if result.data else None
            }
        except Exception as e:
            logger.error(f"Create job error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_job(self, job_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        try:
            query = self.client.table("jobs").select("*").eq("id", job_id)
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Get job error: {str(e)}")
            return None
    
    def get_user_jobs(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's jobs with pagination."""
        try:
            result = self.client.table("jobs").select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Get user jobs error: {str(e)}")
            return []
    
    def update_job(self, job_id: str, data: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Update job data."""
        try:
            query = self.client.table("jobs").update(data).eq("id", job_id)
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            return {
                "success": True,
                "job": result.data[0] if result.data else None
            }
        except Exception as e:
            logger.error(f"Update job error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_plan_limits(self, subscription_tier: str) -> Dict[str, Any]:
        """Get plan limits for a subscription tier."""
        plan_limits = {
            'free': {
                'monthly_limit': 5,
                'file_size_limit': 100 * 1024 * 1024,  # 100MB
                'duration_limit': 300,  # 5 minutes
                'whisper_model': 'base'  # Base model for free tier
            },
            'basic': {
                'monthly_limit': 50,
                'file_size_limit': 500 * 1024 * 1024,  # 500MB
                'duration_limit': 1800,  # 30 minutes
                'whisper_model': 'medium'  # Medium model for basic tier
            },
            'pro': {
                'monthly_limit': 200,
                'file_size_limit': 1024 * 1024 * 1024,  # 1GB
                'duration_limit': 3600,  # 60 minutes
                'whisper_model': 'medium'  # Keep medium for pro
            },
            'enterprise': {
                'monthly_limit': -1,  # Unlimited
                'file_size_limit': 2 * 1024 * 1024 * 1024,  # 2GB
                'duration_limit': 7200,  # 120 minutes
                'whisper_model': 'large'  # Large model for enterprise
            }
        }
        
        return plan_limits.get(subscription_tier, plan_limits['free'])
    
    def increment_api_key_usage(self, api_key_id: str) -> bool:
        """Increment API key usage counter."""
        try:
            # Get current usage
            result = self.client.table("api_keys").select("usage_count").eq("id", api_key_id).execute()
            
            if result.data:
                current_usage = result.data[0].get('usage_count', 0)
                new_usage = current_usage + 1
                
                # Update usage
                self.client.table("api_keys").update({
                    "usage_count": new_usage,
                    "last_used": datetime.utcnow().isoformat()
                }).eq("id", api_key_id).execute()
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Increment API key usage error: {str(e)}")
            return False
    
    # API Key Management
    def create_api_key(self, user_id: str, name: str) -> Dict[str, Any]:
        """Create a new API key using secure utility functions."""
        try:
            from utils.security_utils import generate_secure_api_key
            
            # Validate inputs to prevent database constraint violations
            if len(user_id) > 128:
                logger.error(f"User ID too long: {len(user_id)} chars")
                return {"success": False, "error": "User ID exceeds maximum length"}
            
            if len(name) > 100:
                logger.error(f"API key name too long: {len(name)} chars")
                return {"success": False, "error": "API key name exceeds maximum length"}
            
            # Generate secure API key with our utility function
            raw_key, key_prefix, key_hash = generate_secure_api_key("apf")
            
            # Additional validation for generated key components
            if len(key_hash) > 128:
                logger.error(f"Generated key hash too long: {len(key_hash)} chars")
                return {"success": False, "error": "Generated key hash exceeds database limit"}
            
            api_key_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": name,
                "key_prefix": key_prefix,
                "key_hash": key_hash,
                "is_active": True,
                "usage_count": 0
            }
            
            result = self.client.table("api_keys").insert(api_key_data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "api_key": result.data[0],
                    "raw_key": raw_key  # Only return this once
                }
            
            return {"success": False, "error": "API key creation failed"}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Create API key error: {error_msg}")
            
            # If it's a database constraint error, provide more specific feedback
            if "value too long for type character varying(128)" in error_msg:
                logger.error("Database field length constraint violated")
                return {"success": False, "error": "One of the API key fields exceeds the maximum allowed length"}
            
            return {"success": False, "error": error_msg}
    
    def verify_api_key(self, raw_key: str) -> Optional[Dict[str, Any]]:
        """Verify an API key and return the key data if valid using constant-time comparison."""
        try:
            # Import the secure verification function
            from utils.security_utils import verify_api_key as secure_verify_api_key
            
            # Extract key prefix (first 10 characters) to limit database query
            if not raw_key or len(raw_key) < 10:
                logger.warning("Invalid API key format attempted")
                return None
                
            key_prefix = raw_key[:10]
            
            # Query only keys with matching prefix for better performance
            result = self.client.table("api_keys").select("*")\
                .eq("is_active", True)\
                .eq("key_prefix", key_prefix)\
                .execute()
            
            # If no keys with this prefix, try a broader search as fallback
            if not result.data:
                # Limited fallback query for active keys
                result = self.client.table("api_keys").select("*")\
                    .eq("is_active", True)\
                    .limit(100)\
                    .execute()
            
            # Use constant-time comparison to verify key
            for key_data in result.data or []:
                if secure_verify_api_key(key_data['key_hash'], raw_key):
                    # Update usage count and last used
                    self.client.table("api_keys").update({
                        "usage_count": key_data['usage_count'] + 1,
                        "last_used": datetime.utcnow().isoformat()
                    }).eq("id", key_data['id']).execute()
                    
                    return key_data
            
            # Log failed verification attempt (but don't log the key itself)
            logger.warning(f"API key verification failed for key with prefix {key_prefix[:5]}...")
            return None
        except Exception as e:
            logger.error(f"Verify API key error: {str(e)}")
            return None
    
    def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's API keys."""
        try:
            result = self.client.table("api_keys").select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Get user API keys error: {str(e)}")
            return []
    
    def delete_api_key(self, key_id: str, user_id: str) -> Dict[str, Any]:
        """Delete an API key."""
        try:
            result = self.client.table("api_keys").delete()\
                .eq("id", key_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Delete API key error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Subscription Management
    def create_subscription(self, user_id: str, plan_name: str, plan_price: float) -> Dict[str, Any]:
        """Create a new subscription."""
        try:
            subscription_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "plan_name": plan_name,
                "plan_price": plan_price,
                "status": "pending",
                "is_active": False,
                "auto_renew": True
            }
            
            result = self.client.table("subscriptions").insert(subscription_data).execute()
            return {
                "success": True,
                "subscription": result.data[0] if result.data else None
            }
        except Exception as e:
            logger.error(f"Create subscription error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's active subscription."""
        try:
            result = self.client.table("subscriptions").select("*")\
                .eq("user_id", user_id)\
                .eq("is_active", True)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Get user subscription error: {str(e)}")
            return None
    
    def update_subscription(self, subscription_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update subscription data."""
        try:
            result = self.client.table("subscriptions").update(data).eq("id", subscription_id).execute()
            return {
                "success": True,
                "subscription": result.data[0] if result.data else None
            }
        except Exception as e:
            logger.error(f"Update subscription error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Training Session Management
    def create_training_session(self, user_id: str, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new training session."""
        try:
            training_data['user_id'] = user_id
            training_data['id'] = str(uuid.uuid4())
            
            result = self.client.table("training_sessions").insert(training_data).execute()
            return {
                "success": True,
                "training_session": result.data[0] if result.data else None
            }
        except Exception as e:
            logger.error(f"Create training session error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_training_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's training sessions."""
        try:
            result = self.client.table("training_sessions").select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Get user training sessions error: {str(e)}")
            return []
    
    def ensure_storage_buckets(self):
        """Ensure required storage buckets exist."""
        try:
            required_buckets = ['video-uploads', 'processed-videos']
            
            # Get existing buckets
            existing_buckets = self.client.storage.list_buckets()
            existing_names = [bucket.name for bucket in existing_buckets] if existing_buckets else []
            
            # Create missing buckets
            for bucket_name in required_buckets:
                if bucket_name not in existing_names:
                    try:
                        # Use correct bucket creation parameters
                        self.client.storage.create_bucket(
                            bucket_name,
                            options={
                                'public': False,  # Private buckets for security
                                'file_size_limit': 524288000,  # 500MB in bytes
                                'allowed_mime_types': ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm']
                            }
                        )
                        logger.info(f"Created storage bucket: {bucket_name}")
                    except Exception as create_error:
                        logger.warning(f"Failed to create bucket {bucket_name}: {create_error}")
            
        except Exception as e:
            logger.error(f"Storage bucket initialization error: {str(e)}")
    

# Global service instance
_supabase_service: Optional[SupabaseService] = None

def get_supabase_service() -> SupabaseService:
    """Get or create the global Supabase service instance."""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service

# Export the global instance
supabase_service = get_supabase_service()
