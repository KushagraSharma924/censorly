"""
Security utility functions for file validation and safe handling.
Includes functions for API key security and constant-time comparisons.
"""

import os
import hashlib
import uuid
import hmac
import secrets
import logging
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Try to import magic, fallback if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("python-magic not available, using fallback file validation")

logger = logging.getLogger(__name__)

def get_file_mimetype(file_obj):
    """
    Detect the MIME type of a file using python-magic.
    
    Args:
        file_obj: File object to check
    
    Returns:
        str: MIME type of the file
    """
    if not MAGIC_AVAILABLE:
        # Fallback: use filename extension
        filename = getattr(file_obj, 'filename', '')
        if filename:
            ext = filename.lower().split('.')[-1] if '.' in filename else ''
            extension_mimetypes = {
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo',
                'mov': 'video/quicktime',
                'mkv': 'video/x-matroska',
                'webm': 'video/webm',
                'wmv': 'video/x-ms-wmv'
            }
            return extension_mimetypes.get(ext, 'application/octet-stream')
        return 'application/octet-stream'
    
    try:
        # Save to a temporary location to check with magic
        current_position = file_obj.tell()
        temp_path = f"/tmp/{uuid.uuid4()}"
        file_obj.save(temp_path)
        
        mime = magic.Magic(mime=True)
        mimetype = mime.from_file(temp_path)
        
        # Clean up and reset position
        os.remove(temp_path)
        file_obj.seek(current_position)
        
        return mimetype
    except Exception as e:
        logger.error(f"Error detecting MIME type: {str(e)}")
        # Default to a safe value if detection fails
        return "application/octet-stream"

def validate_video_file(file_obj):
    """
    Validate that a file is actually a video file.
    
    Args:
        file_obj: File object to validate
    
    Returns:
        bool: True if file is a valid video, False otherwise
    """
    mimetype = get_file_mimetype(file_obj)
    
    # Check if mimetype indicates video content
    return mimetype.startswith('video/')

def get_secure_filename(filename):
    """
    Generate a secure filename that keeps the extension.
    
    Args:
        filename: Original filename
    
    Returns:
        str: Secure filename with original extension
    """
    if not filename:
        return str(uuid.uuid4())
        
    # Get the extension
    ext = os.path.splitext(filename)[1].lower() if '.' in filename else ''
    
    # Create a secure base name
    base_name = secure_filename(os.path.splitext(filename)[0])
    if not base_name:
        base_name = str(uuid.uuid4())
    
    # Generate a unique ID and add it to the filename
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{base_name}_{unique_id}{ext}"

def compute_file_hash(file_obj):
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_obj: File object to hash
    
    Returns:
        str: Hex digest of SHA-256 hash
    """
    current_position = file_obj.tell()
    file_obj.seek(0)
    
    sha256 = hashlib.sha256()
    chunk_size = 4096
    
    while True:
        data = file_obj.read(chunk_size)
        if not data:
            break
        sha256.update(data)
    
    file_obj.seek(current_position)
    return sha256.hexdigest()

def is_allowed_extension(filename, allowed_extensions):
    """
    Check if the file has an allowed extension.
    
    Args:
        filename: Filename to check
        allowed_extensions: Set of allowed extensions (with dot)
    
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    if not filename or '.' not in filename:
        return False
        
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def generate_secure_api_key(prefix: str = "apf") -> Tuple[str, str, str]:
    """
    Generate a cryptographically secure API key with prefix.
    
    Returns a tuple of (raw_key, key_prefix, key_hash)
    """
    # Generate a cryptographically secure random string
    raw_key = f"{prefix}_{secrets.token_urlsafe(32)}"
    key_prefix = raw_key[:10]
    
    # Hash the key for secure storage
    key_hash = generate_password_hash(raw_key)
    
    return raw_key, key_prefix, key_hash

def secure_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    This is important when comparing API keys or other security-sensitive strings.
    """
    if val1 is None or val2 is None:
        return False
    
    return hmac.compare_digest(val1, val2)

def verify_api_key(stored_hash: str, provided_key: str) -> bool:
    """
    Verify an API key against a stored hash in constant time.
    
    Args:
        stored_hash: The hash stored in the database
        provided_key: The key provided by the user in the request
        
    Returns:
        bool: True if the key is valid, False otherwise
    """
    if not stored_hash or not provided_key:
        return False
    
    # Use Werkzeug's secure implementation for password hash checking
    # This performs a constant-time comparison to prevent timing attacks
    return check_password_hash(stored_hash, provided_key)
