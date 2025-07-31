"""
Utility functions for application setup and maintenance
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional, Union


def setup_directories(directories: List[Path]) -> None:
    """
    Create directories if they don't exist.
    
    Args:
        directories: List of Path objects to create
    """
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📁 Ensured directory exists: {directory}")


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure basic logging
    handlers: List[Union[logging.StreamHandler, logging.FileHandler]] = [logging.StreamHandler()]
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Reduce noise from some external libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> int:
    """
    Clean up old files in a directory.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours before deletion
        
    Returns:
        Number of files deleted
    """
    import time
    
    if not directory.exists():
        return 0
    
    deleted_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"🗑️ Deleted old file: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {file_path}: {e}")
    
    return deleted_count


def get_disk_usage(path: Path) -> dict:
    """
    Get disk usage statistics for a path.
    
    Args:
        path: Path to check
        
    Returns:
        Dictionary with usage statistics
    """
    import shutil
    
    if not path.exists():
        return {'total': 0, 'used': 0, 'free': 0}
    
    usage = shutil.disk_usage(path)
    return {
        'total': usage.total,
        'used': usage.used,
        'free': usage.free,
        'total_gb': round(usage.total / (1024**3), 2),
        'used_gb': round(usage.used / (1024**3), 2),
        'free_gb': round(usage.free / (1024**3), 2),
        'used_percent': round((usage.used / usage.total) * 100, 1)
    }


def validate_environment() -> dict:
    """
    Validate the environment and dependencies.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'dependencies': {},
        'system': {},
        'errors': []
    }
    
    # Check Python dependencies
    required_packages = [
        'whisper', 'torch', 'ffmpeg-python', 'pydub', 
        'better-profanity', 'flask', 'flask-cors'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            results['dependencies'][package] = 'OK'
        except ImportError:
            results['dependencies'][package] = 'MISSING'
            results['errors'].append(f"Missing dependency: {package}")
    
    # Check system commands
    system_commands = ['ffmpeg', 'ffprobe']
    for cmd in system_commands:
        if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
            results['system'][cmd] = 'OK'
        else:
            results['system'][cmd] = 'MISSING'
            results['errors'].append(f"Missing system command: {cmd}")
    
    return results
