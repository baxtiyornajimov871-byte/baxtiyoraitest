"""
BaxtiyorAiTest - Chat Routes
Main AI Chat API endpoints (ChatGPT-like experience)
"""

from flask import request, jsonify, stream_with_context, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes import chat_bp
from app.services.chat_service import ChatService
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
import time


@chat_bp.route('/new', methods=['POST'])
@jwt_required()
def create_new_chat():
    """Create a new conversation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        conversation = ChatService.create_conversation(
            user_id=user_id,
            title=data.get('title', 'New Chat'),
            model=data.get('model', 'llama3-70b-8192')
        )

        return jsonify({
            "message": "New chat created",
            "conversation": conversation.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_chats():
    """Get all user conversations"""
    try:
        user_id = get_jwt_identity()
        chats = ChatService.get_user_conversations(user_id)
        
        return jsonify({
            "conversations": [chat.to_dict() for chat in chats]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_chat(conversation_id):
    """Get single conversation with messages"""
    try:
        user_id = get_jwt_identity()
        conversation = ChatService.get_conversation_by_id(conversation_id, user_id)
        
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        messages = ChatService.get_conversation_messages(conversation_id, user_id)
        
        return jsonify({
            "conversation": conversation.to_dict(),
            "messages": [msg.to_dict() for msg in messages]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/<int:conversation_id>/message', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send message to AI and get response"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Message content is required"}), 400

        content = data['content']
        model = data.get('model', 'llama3-70b-8192')
        temperature = float(data.get('temperature', 0.7))

        # Save user message
        user_message = ChatService.add_message(
            conversation_id=conversation_id,
            role='user',
            content=content,
            model=model,
            user_id=user_id
        )

        # Get conversation history for context
        history = ChatService.get_recent_messages(conversation_id, limit=10)

        # Generate AI response
        start_time = time.time()
        ai_result = AIService.generate_response(
            prompt=content,
            model=model,
            temperature=temperature,
            conversation_history=[{
                "role": msg.role,
                "content": msg.content
            } for msg in history]
        )

        latency = int((time.time() - start_time) * 1000)

        # Save AI response
        ai_message = ChatService.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=ai_result.get('content', 'Sorry, I could not generate a response.'),
            model=ai_result.get('model'),
            provider=ai_result.get('provider'),
            temperature=temperature
        )

        # Record analytics
        AnalyticsService.record_chat_analytics(
            user_id=user_id,
            conversation_id=conversation_id,
            model=model,
            provider=ai_result.get('provider', 'unknown'),
            tokens=ai_result.get('total_tokens', 0),
            duration_ms=latency
        )

        return jsonify({
            "user_message": user_message.to_dict(),
            "ai_message": ai_message.to_dict(),
            "latency_ms": latency
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/<int:conversation_id>/rename', methods=['PUT'])
@jwt_required()
def rename_chat(conversation_id):
    """Rename conversation"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        conversation = ChatService.update_conversation_title(
            conversation_id, 
            data.get('title', 'Untitled Chat'),
            user_id
        )

        return jsonify({
            "message": "Chat renamed",
            "conversation": conversation.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@chat_bp.route('/<int:conversation_id>/pin', methods=['POST'])
@jwt_required()
def pin_chat(conversation_id):
    """Pin / Unpin conversation"""
    try:
        user_id = get_jwt_identity()
        is_pinned = ChatService.toggle_pin(conversation_id, user_id)
        return jsonify({"is_pinned": is_pinned}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@chat_bp.route('/<int:conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(conversation_id):
    """Delete conversation"""
    try:
        user_id = get_jwt_identity()
        ChatService.delete_conversation(conversation_id, user_id)
        return jsonify({"message": "Conversation deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@chat_bp.route('/search', methods=['GET'])
@jwt_required()
def search_chats():
    """Search conversations"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '')
        
        results = ChatService.search_conversations(user_id, query)
        return jsonify({
            "results": [chat.to_dict() for chat in results]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500