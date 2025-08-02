"""
Supabase integration service for AI Profanity Filter.
Handles direct Supabase operations alongside SQLAlchemy.
"""

import os
from typing import Optional, Dict, Any, List
import logging

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

try:
    from flask import current_app
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

logger = logging.getLogger(__name__)

# Global Supabase client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    
    if not HAS_SUPABASE:
        raise Exception("Supabase client library not installed. Run: pip install supabase")
    
    if _supabase_client is None:
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise Exception("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    
    return _supabase_client


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
