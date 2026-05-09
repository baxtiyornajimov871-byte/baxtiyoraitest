"""
BaxtiyorAiTest - Conversation Routes
Advanced conversation management endpoints
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes import conversation_bp
from app.services.chat_service import ChatService


@conversation_bp.route('/', methods=['GET'])
@jwt_required()
def list_conversations():
    """List all user conversations with filters"""
    try:
        user_id = get_jwt_identity()
        archived = request.args.get('archived', 'false').lower() == 'true'
        favorite = request.args.get('favorite', 'false').lower() == 'true'
        pinned = request.args.get('pinned', 'false').lower() == 'true'

        conversations = ChatService.get_user_conversations(
            user_id=user_id,
            include_archived=archived
        )

        # Apply additional filters
        if favorite:
            conversations = [c for c in conversations if c.is_favorite]
        if pinned:
            conversations = [c for c in conversations if c.is_pinned]

        return jsonify({
            "conversations": [conv.to_dict() for conv in conversations],
            "total": len(conversations)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@conversation_bp.route('/<int:conversation_id>/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite(conversation_id):
    """Toggle favorite status"""
    try:
        user_id = get_jwt_identity()
        is_favorite = ChatService.toggle_favorite(conversation_id, user_id)
        
        return jsonify({
            "message": "Favorite status updated",
            "is_favorite": is_favorite
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@conversation_bp.route('/<int:conversation_id>/archive', methods=['POST'])
@jwt_required()
def archive_conversation(conversation_id):
    """Archive conversation"""
    try:
        user_id = get_jwt_identity()
        ChatService.archive_conversation(conversation_id, user_id)
        
        return jsonify({"message": "Conversation archived successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@conversation_bp.route('/<int:conversation_id>/unarchive', methods=['POST'])
@jwt_required()
def unarchive_conversation(conversation_id):
    """Unarchive conversation"""
    try:
        user_id = get_jwt_identity()
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if conv:
            conv.unarchive()
            return jsonify({"message": "Conversation unarchived"}), 200
        return jsonify({"error": "Conversation not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@conversation_bp.route('/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Get all messages in a conversation"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 100))
        
        messages = ChatService.get_conversation_messages(conversation_id, user_id, limit)
        
        return jsonify({
            "messages": [msg.to_dict() for msg in messages]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@conversation_bp.route('/<int:conversation_id>/regenerate', methods=['POST'])
@jwt_required()
def regenerate_last_message(conversation_id):
    """Regenerate the last AI response"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Get last AI message
        messages = ChatService.get_conversation_messages(conversation_id, user_id, limit=5)
        last_ai_message = next((m for m in reversed(messages) if m.role == 'assistant'), None)
        
        if not last_ai_message:
            return jsonify({"error": "No AI message to regenerate"}), 400

        # Delete last AI message and regenerate
        # (In real implementation you might keep history)
        model = data.get('model', last_ai_message.model)
        
        # Get last user message for regeneration
        last_user_msg = next((m for m in reversed(messages) if m.role == 'user'), None)
        
        if not last_user_msg:
            return jsonify({"error": "No user message found"}), 400

        # Regenerate response (similar logic as send_message)
        ai_result = AIService.generate_response(
            prompt=last_user_msg.content,
            model=model,
            temperature=last_ai_message.temperature or 0.7
        )

        # Save new response
        new_ai_message = ChatService.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=ai_result.get('content'),
            model=ai_result.get('model'),
            provider=ai_result.get('provider')
        )

        return jsonify({
            "message": "Response regenerated",
            "new_message": new_ai_message.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500