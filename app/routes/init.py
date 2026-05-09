"""
BaxtiyorAiTest - Routes Package
Blueprint registration and centralized route management
"""

from flask import Blueprint


def register_blueprints(app):
    """Register all application blueprints"""
    
    # Auth Routes
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # User Routes
    from .user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # Chat & Conversation Routes
    from .chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    from .conversation import conversation_bp
    app.register_blueprint(conversation_bp, url_prefix='/api/conversations')
    
    # Bot & Creator Routes
    from .bot import bot_bp
    app.register_blueprint(bot_bp, url_prefix='/api/bots')
    
    from .creator import creator_bp
    app.register_blueprint(creator_bp, url_prefix='/api/creator')
    
    # Admin Routes
    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Public Routes
    from .public import public_bp
    app.register_blueprint(public_bp, url_prefix='/api/public')
    
    print("✅ All blueprints registered successfully")


# Create blueprints (they will be imported in their respective files)
auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__)
chat_bp = Blueprint('chat', __name__)
conversation_bp = Blueprint('conversation', __name__)
bot_bp = Blueprint('bot', __name__)
creator_bp = Blueprint('creator', __name__)
admin_bp = Blueprint('admin', __name__)
public_bp = Blueprint('public', __name__)