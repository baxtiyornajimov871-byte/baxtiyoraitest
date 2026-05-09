"""
BaxtiyorAiTest - User Service
Business logic for user profile management, updates, and queries
"""

from app.extensions import db
from app.models.user import User
from app.models.creator import CreatorProfile
from werkzeug.utils import secure_filename
import os


class UserService:
    """User Management Service Layer"""

    @staticmethod
    def get_user_by_id(user_id: int):
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str):
        """Get user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def update_profile(user_id: int, data: dict):
        """Update user profile information"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Update basic fields
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'website' in data:
            user.website = data['website']
        if 'github_url' in data:
            user.github_url = data['github_url']
        if 'youtube_url' in data:
            user.youtube_url = data['youtube_url']
        if 'instagram_url' in data:
            user.instagram_url = data['instagram_url']

        db.session.commit()
        return user.to_dict()

    @staticmethod
    def update_avatar(user_id: int, file):
        """Update user avatar"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if not file or not file.filename:
            raise ValueError("No file provided")

        # Secure filename and save
        filename = secure_filename(file.filename)
        unique_filename = f"avatar_{user_id}_{filename}"
        filepath = os.path.join('uploads/avatars', unique_filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)

        # Update user record
        user.avatar = f"/static/uploads/avatars/{unique_filename}"
        db.session.commit()

        return user.avatar

    @staticmethod
    def become_creator(user_id: int, tagline: str = None, about_me: str = None):
        """Convert user to creator"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if user.role.value not in ['user', 'creator']:
            raise ValueError("User cannot become creator")

        # Update role
        user.role = 'creator'
        
        # Create creator profile if not exists
        creator_profile = CreatorProfile.query.filter_by(user_id=user_id).first()
        if not creator_profile:
            creator_profile = CreatorProfile(
                user_id=user_id,
                tagline=tagline,
                about_me=about_me
            )
            db.session.add(creator_profile)
        
        db.session.commit()
        return creator_profile.to_dict()

    @staticmethod
    def get_profile(user_id: int, include_private=False):
        """Get full user profile"""
        user = User.query.get(user_id)
        if not user:
            return None

        profile = user.to_dict(include_sensitive=include_private)
        
        # Add creator profile if exists
        if user.creator_profile:
            profile['creator'] = user.creator_profile.to_dict()
        
        return profile

    @staticmethod
    def search_users(query: str, limit=10):
        """Search users by username or display name"""
        users = User.query.filter(
            db.or_(
                User.username.ilike(f"%{query}%"),
                User.display_name.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        return [user.to_dict() for user in users]

    @staticmethod
    def get_all_users_paginated(page=1, per_page=20, role=None):
        """Admin: Get paginated users"""
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
            
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def ban_user(user_id: int, reason: str = None):
        """Ban user (admin only)"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.is_banned = True
        user.is_active = False
        db.session.commit()
        
        # Logout all sessions
        from .auth_service import AuthService
        AuthService.logout_all_sessions(user_id)
        
        return True

    @staticmethod
    def unban_user(user_id: int):
        """Unban user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.is_banned = False
        user.is_active = True
        db.session.commit()
        return True