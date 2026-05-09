"""
BaxtiyorAiTest - Conversation Model
Manages user chats with advanced features (pin, archive, favorite, search)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class Conversation(BaseModel):
    """Conversation (Chat) Model"""
    
    __tablename__ = 'conversations'
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Basic Info
    title = Column(String(200), nullable=False, default="New Chat")
    slug = Column(String(100), nullable=True, unique=True)  # For sharing
    
    # Status flags
    is_pinned = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Metadata
    model_used = Column(String(100), default="llama3-70b-8192")  # Last used model
    temperature = Column(Float, default=0.7)
    category = Column(String(50), nullable=True)  # e.g., "Work", "Creative", "Study"
    
    # Statistics
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='conversations')
    messages = relationship('Message', 
                          back_populates='conversation', 
                          cascade="all, delete-orphan",
                          order_by="Message.created_at")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_user_pinned', 'user_id', 'is_pinned'),
        Index('idx_user_archived', 'user_id', 'is_archived'),
        Index('idx_user_favorite', 'user_id', 'is_favorite'),
    )
    
    def update_title(self, new_title: str):
        """Update conversation title"""
        self.title = new_title[:200]
        self.save()
    
    def increment_message_count(self):
        """Update message counter and timestamp"""
        self.message_count += 1
        self.last_message_at = datetime.utcnow()
        db.session.commit()
    
    def toggle_pin(self):
        """Pin / Unpin conversation"""
        self.is_pinned = not self.is_pinned
        self.save()
    
    def toggle_favorite(self):
        """Add / Remove from favorites"""
        self.is_favorite = not self.is_favorite
        self.save()
    
    def archive(self):
        """Archive conversation"""
        self.is_archived = True
        self.save()
    
    def unarchive(self):
        """Unarchive conversation"""
        self.is_archived = False
        self.save()
    
    def soft_delete(self):
        """Soft delete conversation"""
        self.is_deleted = True
        self.save()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "user_id": self.user_id,
            "model_used": self.model_used,
            "temperature": self.temperature,
            "is_pinned": self.is_pinned,
            "is_favorite": self.is_favorite,
            "is_archived": self.is_archived,
            "message_count": self.message_count,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.title} (User {self.user_id})>'