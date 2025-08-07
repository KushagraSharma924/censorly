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
        self.supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise Exception("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Supabase service initialized successfully")
    
    # User Management
    async def create_user(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Create a new user with Supabase Auth."""
        try:
            # Create user with Supabase Auth
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })
            
            if auth_response.user:
                # Insert additional user data into our users table
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "password_hash": generate_password_hash(password),
                    "subscription_tier": "free",
                    "is_active": True,
                    "is_verified": False
                }
                
                result = self.client.table("users").insert(user_data).execute()
                
                return {
                    "success": True,
                    "user": result.data[0] if result.data else None,
                    "auth_user": auth_response.user
                }
            
            return {"success": False, "error": "User creation failed"}
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Supabase Auth."""
        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Get user data from our users table
                user_data = self.client.table("users").select("*").eq("id", auth_response.user.id).execute()
                
                # Update last login
                self.client.table("users").update({
                    "last_login": datetime.utcnow().isoformat()
                }).eq("id", auth_response.user.id).execute()
                
                return {
                    "success": True,
                    "user": user_data.data[0] if user_data.data else None,
                    "session": auth_response.session,
                    "access_token": auth_response.session.access_token if auth_response.session else None
                }
            
            return {"success": False, "error": "Invalid credentials"}
            
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


def get_service_client() -> Client:
    """Get Supabase client with service role key for admin operations."""
    if not HAS_SUPABASE:
        raise Exception("Supabase client library not installed. Run: pip install supabase")
        
    supabase_url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        raise Exception("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
    
    return create_client(supabase_url, service_key)


class SupabaseService:
    """Service class for Supabase operations."""
    
    def __init__(self):
        try:
            self.client = get_supabase_client()
            self.service_client = get_service_client()
            self.available = True
        except Exception as e:
            logger.warning(f"Supabase service initialization failed: {e}")
            self.client = None
            self.service_client = None
            self.available = False
    
    def test_connection(self) -> bool:
        """Test Supabase connection."""
        if not self.available or not self.client:
            return False
            
        try:
            # Test with a simple query
            result = self.client.table('users').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def create_user(self, email: str, password: str, **kwargs) -> Dict[str, Any]:
        """Create a new user in Supabase Auth."""
        try:
            response = self.service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": kwargs
            })
            return response
        except Exception as e:
            logger.error(f"Failed to create user in Supabase: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from Supabase Auth."""
        try:
            response = self.service_client.auth.admin.get_user_by_id(user_id)
            return response.user if response else None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Update user metadata in Supabase Auth."""
        try:
            self.service_client.auth.admin.update_user_by_id(
                user_id, 
                {"user_metadata": metadata}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update user metadata: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user from Supabase Auth."""
        try:
            self.service_client.auth.admin.delete_user(user_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False
    
    def store_file(self, bucket: str, file_path: str, file_data: bytes) -> Optional[str]:
        """Store file in Supabase Storage."""
        try:
            response = self.client.storage.from_(bucket).upload(file_path, file_data)
            if response:
                return self.client.storage.from_(bucket).get_public_url(file_path)
            return None
        except Exception as e:
            logger.error(f"Failed to store file: {e}")
            return None
    
    def get_file_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Get public URL for file in Supabase Storage."""
        try:
            return self.client.storage.from_(bucket).get_public_url(file_path)
        except Exception as e:
            logger.error(f"Failed to get file URL: {e}")
            return None
    
    def delete_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from Supabase Storage."""
        try:
            response = self.client.storage.from_(bucket).remove([file_path])
            return len(response) > 0
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False


# Global service instance
_supabase_service = None

def get_supabase_service():
    """Get or create global Supabase service instance."""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service

# For backward compatibility
supabase_service = None  # Will be initialized when first accessed


def init_supabase_tables():
    """Initialize required tables in Supabase if they don't exist."""
    try:
        client = get_service_client()
        
        # Check if tables exist by querying them
        tables_to_check = ['users', 'jobs', 'training_sessions']
        
        for table in tables_to_check:
            try:
                client.table(table).select('*').limit(1).execute()
                logger.info(f"Table '{table}' exists")
            except Exception:
                logger.warning(f"Table '{table}' might not exist - SQLAlchemy will handle creation")
        
        return True
    except Exception as e:
        logger.error(f"Failed to check Supabase tables: {e}")
        return False


def setup_supabase_storage():
    """Setup required storage buckets."""
    try:
        client = get_service_client()
        
        # Create buckets for file storage
        buckets = ['videos', 'processed-videos', 'models']
        
        for bucket in buckets:
            try:
                client.storage.create_bucket(bucket, {"name": bucket, "public": False})
                logger.info(f"Created bucket: {bucket}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"Bucket '{bucket}' already exists")
                else:
                    logger.error(f"Failed to create bucket '{bucket}': {e}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to setup Supabase storage: {e}")
        return False
