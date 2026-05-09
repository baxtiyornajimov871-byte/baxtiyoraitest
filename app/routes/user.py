"""
BaxtiyorAiTest - User Routes
User profile, settings, and account management endpoints
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes import user_bp
from app.services.user_service import UserService
from app.services.creator_service import CreatorService


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        profile = UserService.get_profile(user_id, include_private=True)
        
        if not profile:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(profile), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        updated_user = UserService.update_profile(user_id, data)
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": updated_user
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500


@user_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Upload user avatar"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        user_id = get_jwt_identity()
        
        avatar_url = UserService.update_avatar(user_id, file)
        
        return jsonify({
            "message": "Avatar updated successfully",
            "avatar_url": avatar_url
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to upload avatar"}), 500


@user_bp.route('/become-creator', methods=['POST'])
@jwt_required()
def become_creator():
    """Convert user account to creator"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        creator_profile = UserService.become_creator(
            user_id=user_id,
            tagline=data.get('tagline'),
            about_me=data.get('about_me')
        )
        
        return jsonify({
            "message": "You are now a creator!",
            "creator_profile": creator_profile
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to become creator"}), 500


@user_bp.route('/<string:username>', methods=['GET'])
def get_public_profile(username):
    """Get public user/creator profile"""
    try:
        user = UserService.get_user_by_username(username)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        profile = UserService.get_profile(user.id)
        return jsonify(profile), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not all(k in data for k in ['old_password', 'new_password']):
            return jsonify({"error": "Old and new password required"}), 400

        UserService.change_password(
            user_id=user_id,
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        
        return jsonify({"message": "Password changed successfully. Please login again."}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to change password"}), 500


@user_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users"""
    try:
        query = request.args.get('q', '')
        if len(query) < 2:
            return jsonify({"users": []}), 200
            
        users = UserService.search_users(query, limit=10)
        return jsonify({"users": users}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500