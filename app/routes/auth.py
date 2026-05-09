"""
BaxtiyorAiTest - Authentication Routes
Full JWT Auth API with Register, Login, Logout, Refresh
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.routes import auth_bp
from app.services.auth_service import AuthService
from app.middleware.rate_limit import rate_limit


@auth_bp.route('/register', methods=['POST'])
@rate_limit(limit=5, per=60)  # 5 registrations per minute
def register():
    """User Registration"""
    try:
        data = request.get_json()
        
        required = ['username', 'email', 'password']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400

        user = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            display_name=data.get('display_name')
        )

        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit(limit=10, per=60)
def login():
    """User Login"""
    try:
        data = request.get_json()
        user_agent = request.headers.get('User-Agent')
        ip = request.remote_addr

        result = AuthService.login_user(
            email=data['email'],
            password=data['password'],
            user_agent=user_agent,
            ip_address=ip
        )

        return jsonify({
            "message": "Login successful",
            **result
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception:
        return jsonify({"error": "Login failed"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh Access Token"""
    try:
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        
        return jsonify({
            "access_token": new_access_token
        }), 200
    except Exception:
        return jsonify({"error": "Token refresh failed"}), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout - Revoke current token"""
    try:
        jti = get_jwt()['jti']
        AuthService.logout_user(jti)
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception:
        return jsonify({"error": "Logout failed"}), 500


@auth_bp.route('/logout-all', methods=['POST'])
@jwt_required()
def logout_all():
    """Logout from all devices"""
    try:
        user_id = get_jwt_identity()
        AuthService.logout_all_sessions(user_id)
        return jsonify({"message": "Logged out from all devices"}), 200
    except Exception:
        return jsonify({"error": "Failed to logout all sessions"}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict(include_sensitive=True)), 200