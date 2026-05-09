"""
BaxtiyorAiTest - Auth Service
Enterprise-grade authentication business logic layer
"""

from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from app.extensions import db
from app.models.user import User
from app.models.session import UserSession
import uuid


class AuthService:
    """Authentication Service Layer"""

    @staticmethod
    def register_user(username: str, email: str, password: str, display_name: str = None):
        """Register new user"""
        if User.query.filter_by(username=username).first():
            raise ValueError("Username already taken")
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")

        user = User(
            username=username,
            email=email,
            display_name=display_name or username
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user

    @staticmethod
    def login_user(email: str, password: str, user_agent: str = None, ip_address: str = None):
        """Login user and create session"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if user.is_banned:
            raise ValueError("Account has been banned")
        
        if not user.check_password(password):
            user.increment_failed_login()
            raise ValueError("Invalid credentials")
        
        # Reset failed attempts on successful login
        user.reset_failed_login()
        user.update_last_login()
        
        # Create JWT tokens
        identity = user.id
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        # Create session record
        jti = get_jti(encoded_token=access_token)
        
        session = UserSession(
            user_id=user.id,
            session_token=jti,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_in=3600
        )
        db.session.add(session)
        db.session.commit()
        
        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session.id
        }

    @staticmethod
    def refresh_token(refresh_token: str):
        """Refresh access token"""
        # JWT Extended handles refresh logic automatically in routes
        # This method can be extended for custom logic
        pass

    @staticmethod
    def logout_user(jti: str):
        """Logout user by revoking token"""
        session = UserSession.query.filter_by(session_token=jti).first()
        if session:
            session.revoke()
        return True

    @staticmethod
    def logout_all_sessions(user_id: int):
        """Force logout from all devices"""
        UserSession.revoke_all_sessions(user_id)
        return True

    @staticmethod
    def is_token_revoked(jti: str) -> bool:
        """Check if token is revoked (used by JWT extension)"""
        session = UserSession.query.filter_by(session_token=jti, is_active=True).first()
        if not session:
            return True
        return session.is_expired()

    @staticmethod
    def get_user_by_id(user_id: int):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email: str):
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        """Change user password"""
        user = User.query.get(user_id)
        if not user or not user.check_password(old_password):
            raise ValueError("Current password is incorrect")
        
        user.set_password(new_password)
        db.session.commit()
        # Logout all sessions after password change
        AuthService.logout_all_sessions(user_id)
        return True