"""
BaxtiyorAiTest - Chat WebSocket Handler
Real-time AI response streaming support
"""

from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_service import AIService
from app.services.chat_service import ChatService


def register_socket_events(socketio):
    """Register all socket events"""

    @socketio.on('connect')
    def handle_connect():
        print("Client connected to WebSocket")
        emit('status', {'message': 'Connected to BaxtiyorAiTest real-time server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print("Client disconnected")

    @socketio.on('join_chat')
    @jwt_required()
    def handle_join_chat(data):
        """Join a conversation room"""
        conversation_id = data.get('conversation_id')
        user_id = get_jwt_identity()
        
        if conversation_id:
            room = f"chat_{conversation_id}"
            join_room(room)
            emit('joined', {
                'conversation_id': conversation_id,
                'message': f'Joined chat {conversation_id}'
            }, room=room)

    @socketio.on('send_message')
    @jwt_required()
    def handle_send_message(data):
        """Handle real-time message and stream AI response"""
        try:
            user_id = get_jwt_identity()
            conversation_id = data.get('conversation_id')
            content = data.get('content')
            model = data.get('model', 'llama3-70b-8192')
            temperature = float(data.get('temperature', 0.7))

            if not conversation_id or not content:
                emit('error', {'message': 'Missing conversation_id or content'})
                return

            # Save user message
            user_message = ChatService.add_message(
                conversation_id=conversation_id,
                role='user',
                content=content,
                model=model,
                user_id=user_id
            )

            room = f"chat_{conversation_id}"
            emit('user_message', user_message.to_dict(), room=room)

            # Start streaming AI response
            emit('ai_start', {'message': 'AI is thinking...'}, room=room)

            # Get conversation history
            history = ChatService.get_recent_messages(conversation_id, limit=12)
            
            # Generate response (streaming simulation)
            ai_result = AIService.generate_response(
                prompt=content,
                model=model,
                temperature=temperature,
                conversation_history=[{
                    "role": msg.role,
                    "content": msg.content
                } for msg in history]
            )

            # Send final response
            ai_message = ChatService.add_message(
                conversation_id=conversation_id,
                role='assistant',
                content=ai_result.get('content', 'Sorry, I could not generate a response.'),
                model=ai_result.get('model'),
                provider=ai_result.get('provider')
            )

            emit('ai_response', ai_message.to_dict(), room=room)

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('typing')
    def handle_typing(data):
        """Show typing indicator"""
        room = f"chat_{data.get('conversation_id')}"
        emit('user_typing', {
            'user_id': get_jwt_identity(),
            'is_typing': data.get('is_typing', True)
        }, room=room, include_self=False)


# This function will be called from app/__init__.py
# socketio = SocketIO(app)
# register_socket_events(socketio)