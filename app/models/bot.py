"""
BaxtiyorAiTest - Custom AI Bot Model
Character.AI style custom bots created by users
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
import uuid

from .base import BaseModel
from app.extensions import db


class Bot(BaseModel):
    """Custom AI Bot Model"""
    
    __tablename__ = 'bots'
    
    # Owner
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Visuals
    avatar = Column(String(255), nullable=True, default="default_bot_avatar.png")
    banner = Column(String(255), nullable=True)
    
    # Bot Configuration
    system_prompt = Column(Text, nullable=False)
    greeting_message = Column(String(500), default="Hello! How can I help you today?")
    temperature = Column(Float, default=0.8)
    max_tokens = Column(Integer, default=2048)
    
    # Categorization
    category = Column(String(50), nullable=True)  # e.g., "Assistant", "Roleplay", "Tutor", "Creative"
    tags = Column(JSON, default=list)  # ["fun", "serious", "coding"]
    
    # Visibility & Status
    visibility = Column(String(20), default="public")  # public, private, unlisted
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    usage_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    
    # Relationships
    owner = relationship('User', back_populates='created_bots')
    likes = relationship('Like', back_populates='bot', cascade="all, delete-orphan")
    bookmarks = relationship('Bookmark', back_populates='bot', cascade="all, delete-orphan")
    
    def __init__(self, owner_id, name, description, system_prompt, **kwargs):
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.slug = kwargs.get('slug') or self.generate_slug(name)
        self.category = kwargs.get('category')
        self.tags = kwargs.get('tags', [])
        self.temperature = kwargs.get('temperature', 0.8)
        self.greeting_message = kwargs.get('greeting_message', "Hello! How can I help you today?")
    
    def generate_slug(self, name: str) -> str:
        """Generate unique slug from bot name"""
        base_slug = name.lower().strip().replace(" ", "-")
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_slug}-{unique_id}"
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        db.session.commit()
    
    def increment_likes(self):
        """Increment likes count"""
        self.likes_count += 1
        db.session.commit()
    
    def decrement_likes(self):
        """Decrement likes count"""
        if self.likes_count > 0:
            self.likes_count -= 1
            db.session.commit()
    
    def to_dict(self, include_owner=False):
        """Convert bot to dictionary for API"""
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "avatar": self.avatar,
            "banner": self.banner,
            "category": self.category,
            "tags": self.tags,
            "visibility": self.visibility,
            "is_verified": self.is_verified,
            "usage_count": self.usage_count,
            "likes_count": self.likes_count,
            "temperature": self.temperature,
            "greeting_message": self.greeting_message,
            "created_at": self.created_at.isoformat()
        }
        
        if include_owner:
            data["owner"] = {
                "id": self.owner.id,
                "username": self.owner.username,
                "display_name": self.owner.display_name,
                "avatar": self.owner.avatar
            }
        
        return data
    
    def __repr__(self):
        return f'<Bot {self.id}: {self.name} by User {self.owner_id}>'