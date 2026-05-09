"""
BaxtiyorAiTest - Security Utilities
Input sanitization, validation, and security helpers
"""

import re
import html
from bleach import clean
import uuid
from werkzeug.utils import secure_filename as werkzeug_secure_filename


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text:
        return ""
    
    # Escape HTML
    text = html.escape(text)
    
    # Clean with bleach (remove dangerous tags)
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'code', 'pre']
    allowed_attributes = {}
    
    text = clean(text, tags=allowed_tags, attributes=allowed_attributes)
    
    return text.strip()


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or len(email) > 120:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def secure_filename_custom(filename: str) -> str:
    """More secure filename generation"""
    if not filename:
        return ""
    
    # Get extension
    ext = ""
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
    
    # Generate safe name with UUID
    safe_name = werkzeug_secure_filename(filename)
    unique_name = f"{uuid.uuid4().hex[:16]}_{safe_name}"
    
    if ext:
        return unique_name
    return unique_name


def validate_password_strength(password: str) -> tuple:
    """Check password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"


def sanitize_filename_for_url(filename: str) -> str:
    """Prepare filename for safe URL usage"""
    name = secure_filename_custom(filename)
    return name.replace(" ", "_").lower()


def is_safe_url(url: str) -> bool:
    """Basic check for safe redirect URLs"""
    if not url:
        return False
    return url.startswith('/') or url.startswith('http://127.0.0.1') or url.startswith('http://localhost')


def strip_html_tags(text: str) -> str:
    """Remove all HTML tags"""
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text.strip()