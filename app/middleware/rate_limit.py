"""
BaxtiyorAiTest - Rate Limiting Middleware
Advanced rate limiting for different endpoints
"""

from functools import wraps
from flask import request, jsonify
from flask_limiter import Limiter
from app.extensions import limiter


def rate_limit(limit="100 per minute", key_func=None):
    """
    Custom rate limit decorator with flexible limits
    """
    def decorator(f):
        @wraps(f)
        @limiter.limit(limit, key_func=key_func)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Specific rate limits for sensitive endpoints
def auth_rate_limit(f):
    """Strict rate limit for authentication endpoints"""
    return rate_limit(limit="10 per minute")(f)


def api_rate_limit(f):
    """General API rate limit"""
    return rate_limit(limit="60 per minute")(f)


def chat_rate_limit(f):
    """Rate limit for AI chat endpoints (more restrictive)"""
    return rate_limit(limit="30 per minute")(f)


def upload_rate_limit(f):
    """Rate limit for file uploads"""
    return rate_limit(limit="10 per 5 minutes")(f)


# Custom key function for more intelligent limiting
def user_id_key():
    """Use user ID for rate limiting when authenticated"""
    from flask_jwt_extended import get_jwt_identity
    try:
        return get_jwt_identity() or request.remote_addr
    except:
        return request.remote_addr


def ip_key():
    """Fallback to IP address"""
    return request.remote_addr