"""
BaxtiyorAiTest - Admin Routes
Full Admin Dashboard API with analytics, moderation, and system management
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes import admin_bp
from app.services.analytics_service import AnalyticsService
from app.services.user_service import UserService
from app.services.chat_service import ChatService


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Main Admin Dashboard Statistics"""
    try:
        user_id = get_jwt_identity()
        from app.models.user import User
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        stats = AnalyticsService.get_system_dashboard_stats()
        recent_activities = AnalyticsService.get_recent_activities(limit=15)
        provider_stats = AnalyticsService.get_provider_usage_stats()
        top_bots = AnalyticsService.get_top_bots(limit=10)

        return jsonify({
            "system_stats": stats,
            "provider_stats": provider_stats,
            "top_bots": [bot.to_dict() for bot in top_bots],
            "recent_activities": [activity.to_dict() for activity in recent_activities]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Admin: Get all users with pagination"""
    try:
        user_id = get_jwt_identity()
        from app.models.user import User
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        role = request.args.get('role')

        pagination = UserService.get_all_users_paginated(page, per_page, role)
        
        return jsonify({
            "users": [user.to_dict(include_sensitive=True) for user in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@jwt_required()
def ban_user(user_id):
    """Ban a user"""
    try:
        admin_id = get_jwt_identity()
        from app.models.user import User
        admin = User.query.get(admin_id)
        
        if not admin or admin.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        data = request.get_json() or {}
        reason = data.get('reason', 'Violated community guidelines')

        UserService.ban_user(user_id, reason)
        
        return jsonify({"message": f"User {user_id} has been banned"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@jwt_required()
def unban_user(user_id):
    """Unban a user"""
    try:
        admin_id = get_jwt_identity()
        from app.models.user import User
        admin = User.query.get(admin_id)
        
        if not admin or admin.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        UserService.unban_user(user_id)
        
        return jsonify({"message": f"User {user_id} has been unbanned"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.route('/conversations/<int:conversation_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_conversation_admin(conversation_id):
    """Admin: Force delete any conversation"""
    try:
        admin_id = get_jwt_identity()
        from app.models.user import User
        admin = User.query.get(admin_id)
        
        if not admin or admin.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        # For simplicity we mark as deleted (can be extended to hard delete)
        conv = ChatService.get_conversation_by_id(conversation_id)
        if conv:
            conv.soft_delete()
            return jsonify({"message": "Conversation deleted by admin"}), 200
        
        return jsonify({"error": "Conversation not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/analytics/provider', methods=['GET'])
@jwt_required()
def provider_analytics():
    """Get AI provider usage analytics"""
    try:
        user_id = get_jwt_identity()
        from app.models.user import User
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role.value not in ['admin', 'super_admin']:
            return jsonify({"error": "Admin access required"}), 403

        stats = AnalyticsService.get_provider_usage_stats()
        return jsonify({"provider_usage": stats}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_system_logs():
    """View recent system logs (for super admin)"""
    try:
        user_id = get_jwt_identity()
        from app.models.user import User
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role.value != 'super_admin':
            return jsonify({"error": "Super Admin access required"}), 403

        # In production, read from log files
        return jsonify({
            "message": "System logs endpoint ready",
            "note": "Full log viewer will be implemented with file reading"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500