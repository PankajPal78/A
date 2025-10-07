"""
Utility functions and helpers
"""

import os
import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

def setup_logging(log_level: str = 'INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('rag_system.log')
        ]
    )

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration"""
    issues = []
    warnings = []
    
    # Check required directories
    required_dirs = ['uploads', 'chroma_db']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                warnings.append(f"Created missing directory: {dir_name}")
            except Exception as e:
                issues.append(f"Cannot create directory {dir_name}: {str(e)}")
    
    # Check API keys
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not gemini_key and not openai_key:
        issues.append("No LLM API keys found. Set GEMINI_API_KEY or OPENAI_API_KEY")
    elif not gemini_key:
        warnings.append("GEMINI_API_KEY not set")
    elif not openai_key:
        warnings.append("OPENAI_API_KEY not set")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

def create_error_response(message: str, status_code: int = 500, 
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        'error': message,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }