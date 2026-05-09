"""
BaxtiyorAiTest - WebSocket / Sockets Package
Future real-time streaming support (for AI response streaming)
"""

from flask_socketio import SocketIO

# Initialize SocketIO (will be attached in app/__init__.py later)
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='gevent',           # Better performance with Gunicorn + Gevent
    logger=True,
    engineio_logger=True
)

# Import socket events
from .chat_socket import register_socket_events

__all__ = ['socketio', 'register_socket_events']