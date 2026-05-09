"""
BaxtiyorAiTest - Authentication Middleware
Role-based access control decorators
"""

from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from app.models.user import User


def admin_required(f):
    """Decorator for Admin and Super Admin only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role.value not in ['admin', 'super_admin']:
                return jsonify({"error": "Admin access required"}), 403
            
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Authentication failed"}), 401
    return decorated_function


def super_admin_required(f):
    """Decorator for Super Admin only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role.value != 'super_admin':
                return jsonify({"error": "Super Admin access required"}), 403
            
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Authentication failed"}), 401
    return decorated_function


def creator_required(f):
    """Decorator for Creator level access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role.value not in ['creator', 'admin', 'super_admin']:
                return jsonify({"error": "Creator access required"}), 403
            
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Authentication failed"}), 401
    return decorated_function


def jwt_optional(f):
    """Optional JWT - works with or without token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            return f(*args, **kwargs)
    return decorated_function