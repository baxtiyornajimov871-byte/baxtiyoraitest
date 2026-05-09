"""
BaxtiyorAiTest - Creator Routes
Creator profile, dashboard, and public creator pages
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes import creator_bp
from app.services.creator_service import CreatorService
from app.services.user_service import UserService


@creator_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_my_creator_profile():
    """Get current user's creator profile"""
    try:
        user_id = get_jwt_identity()
        profile = CreatorService.get_creator_profile(user_id)
        
        if not profile:
            return jsonify({"error": "You are not a creator yet"}), 403
        
        return jsonify(profile.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@creator_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_creator_profile():
    """Update creator profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        updated_profile = CreatorService.update_creator_profile(user_id, data)
        
        return jsonify({
            "message": "Creator profile updated successfully",
            "profile": updated_profile
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update profile"}), 500


@creator_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def creator_dashboard():
    """Creator Dashboard - Full statistics and bots"""
    try:
        user_id = get_jwt_identity()
        dashboard_data = CreatorService.get_creator_dashboard(user_id)
        
        return jsonify(dashboard_data), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "Failed to load dashboard"}), 500


@creator_bp.route('/<string:username>', methods=['GET'])
def get_public_creator(username):
    """Public Creator Profile Page"""
    try:
        profile = CreatorService.get_public_creator_profile(username)
        if not profile:
            return jsonify({"error": "Creator not found"}), 404
        
        return jsonify(profile), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@creator_bp.route('/featured', methods=['GET'])
def get_featured_creators():
    """Get featured creators for homepage/marketplace"""
    try:
        creators = CreatorService.get_featured_creators(limit=12)
        return jsonify({
            "creators": [c.to_dict() for c in creators]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@creator_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_creator():
    """Admin only: Verify a creator"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # In real app, check if current user is admin
        from app.models.user import User
        current_user = User.query.get(user_id)
        if not current_user or current_user.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        target_user_id = data.get('user_id')
        reason = data.get('reason')
        
        CreatorService.verify_creator(target_user_id, user_id, reason)
        
        return jsonify({"message": "Creator verified successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Verification failed"}), 500


@creator_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_creators():
    """Admin: Get all creators with pagination"""
    try:
        user_id = get_jwt_identity()
        from app.models.user import User
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        pagination = CreatorService.get_all_creators_paginated(page, per_page)
        
        return jsonify({
            "creators": [c.to_dict() for c in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500