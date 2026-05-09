"""
BaxtiyorAiTest - General Helper Functions
Common utilities used across the application
"""

from datetime import datetime
import re


def generate_slug(text: str, max_length: int = 100) -> str:
    """Generate URL-friendly slug from text"""
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces
    slug = text.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special characters
    slug = re.sub(r'[\s-]+', '-', slug)       # Replace spaces and multiple dashes
    slug = slug[:max_length].strip('-')
    
    return slug


def format_timestamp(dt: datetime, format_type: str = "full") -> str:
    """Format datetime for frontend display"""
    if not dt:
        return ""
    
    if format_type == "full":
        return dt.strftime("%B %d, %Y at %I:%M %p")
    elif format_type == "short":
        return dt.strftime("%b %d, %Y")
    elif format_type == "time":
        return dt.strftime("%I:%M %p")
    elif format_type == "relative":
        # Simple relative time (can be enhanced with dateutil)
        delta = datetime.utcnow() - dt
        if delta.days > 30:
            return dt.strftime("%b %d, %Y")
        elif delta.days > 1:
            return f"{delta.days} days ago"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.seconds // 3600 > 1:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds // 60 > 1:
            return f"{delta.seconds // 60} minutes ago"
        else:
            return "Just now"
    
    return dt.isoformat()


def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_name[i]}"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + suffix


def generate_unique_code(length: int = 8) -> str:
    """Generate random alphanumeric code"""
    import random
    import string
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_client_ip(request) -> str:
    """Get real client IP considering proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr


def is_valid_uuid(uuid_str: str) -> bool:
    """Validate UUID string"""
    try:
        import uuid
        uuid.UUID(str(uuid_str))
        return True
    except:
        return False