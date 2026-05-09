"""
BaxtiyorAiTest - Flask Extensions
Centralized extension initialization for the application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

# Initialize extensions (without binding to app yet)
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

# Rate Limiter with custom key function
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Change to Redis in production
    strategy="fixed-window"
)

# Custom JWT claims loader (for future use)
@jwt.user_identity_loader
def user_identity_lookup(user):
    """Return user ID for JWT identity"""
    return user.id if hasattr(user, 'id') else user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from JWT token"""
    from app.models.user import User
    identity = jwt_data["sub"]
    return User.query.get(identity)


# Token blocklist loader (for logout functionality)
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """Check if token is in blocklist (for secure logout)"""
    from app.services.auth_service import AuthService
    jti = jwt_payload["jti"]
    return AuthService.is_token_revoked(jti)