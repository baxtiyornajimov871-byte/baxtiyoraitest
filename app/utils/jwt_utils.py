"""
BaxtiyorAiTest - JWT Utilities
Helper functions for JWT token management
"""

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta


def generate_tokens(user_id: int, additional_claims: dict = None):
    """Generate both access and refresh tokens"""
    if additional_claims is None:
        additional_claims = {}
    
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=30)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def decode_jwt(token: str):
    """Safely decode JWT token"""
    try:
        decoded = decode_token(token)
        return decoded
    except Exception as e:
        return None


def get_token_expiration(token: str):
    """Get expiration time from token"""
    try:
        decoded = decode_token(token, allow_expired=True)
        exp_timestamp = decoded.get('exp')
        if exp_timestamp:
            return datetime.utcfromtimestamp(exp_timestamp)
        return None
    except:
        return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired"""
    exp = get_token_expiration(token)
    if not exp:
        return True
    return datetime.utcnow() > exp


def extract_jti(token: str):
    """Extract JWT ID (jti) from token"""
    try:
        decoded = decode_token(token, allow_expired=True)
        return decoded.get('jti')
    except:
        return None