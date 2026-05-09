"""
BaxtiyorAiTest - User Model
Enterprise-grade User model with full authentication and profile features
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from werkzeug.security import generate_password_hash, check_password_hash

from .base import BaseModel
from app.extensions import db


class UserRole(str, enum.Enum):
    USER = "user"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(BaseModel):
    """Main User Model"""
    
    __tablename__ = 'users'
    
    # Authentication fields
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile fields
    display_name = Column(String(100), nullable=True)
    avatar = Column(String(255), nullable=True, default="default_avatar.png")
    bio = Column(Text, nullable=True)
    
    # Social links
    website = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    youtube_url = Column(String(255), nullable=True)
    instagram_url = Column(String(255), nullable=True)
    
    # Role & Status
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Activity tracking
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    
    # Relationships
    conversations = relationship('Conversation', back_populates='user', cascade="all, delete-orphan")
    messages = relationship('Message', back_populates='user', cascade="all, delete-orphan")
    uploads = relationship('Upload', back_populates='user', cascade="all, delete-orphan")
    created_bots = relationship('Bot', back_populates='owner', cascade="all, delete-orphan")
    creator_profile = relationship('CreatorProfile', uselist=False, back_populates='user')
    
    # Likes & Bookmarks
    likes = relationship('Like', back_populates='user', cascade="all, delete-orphan")
    bookmarks = relationship('Bookmark', back_populates='user', cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update login timestamp and count"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        db.session.commit()
    
    def increment_failed_login(self):
        """Track failed login attempts"""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login counter"""
        self.failed_login_attempts = 0
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email if include_sensitive else None,
            "avatar": self.avatar,
            "bio": self.bio,
            "role": self.role.value,
            "is_verified": self.is_verified,
            "is_banned": self.is_banned,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count
        }
        return data
    
    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'