"""
BaxtiyorAiTest - Bookmark Model
For users to bookmark their favorite custom bots
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class Bookmark(BaseModel):
    """Bookmark Model - User bookmarks on bots"""
    
    __tablename__ = 'bookmarks'
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    bot_id = Column(Integer, ForeignKey('bots.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Additional info
    note = Column(Text, nullable=True)  # Optional user note about the bookmark
    
    # Relationships
    user = relationship('User', back_populates='bookmarks')
    bot = relationship('Bot', back_populates='bookmarks')
    
    # Unique constraint: one user can bookmark a bot only once
    __table_args__ = (
        UniqueConstraint('user_id', 'bot_id', name='uq_user_bot_bookmark'),
    )
    
    def __init__(self, user_id: int, bot_id: int, note: str = None):
        self.user_id = user_id
        self.bot_id = bot_id
        self.note = note
    
    @classmethod
    def toggle_bookmark(cls, user_id: int, bot_id: int, note: str = None):
        """Toggle bookmark (add if not exists, remove if exists)"""
        existing = cls.query.filter_by(user_id=user_id, bot_id=bot_id).first()
        
        if existing:
            # Remove bookmark
            existing.delete()
            if hasattr(existing.bot, 'bookmark_count'):
                existing.bot.bookmark_count = max(0, existing.bot.bookmark_count - 1)
                db.session.commit()
            return False  # removed
        else:
            # Add bookmark
            bookmark = cls(user_id=user_id, bot_id=bot_id, note=note)
            bookmark.save()
            
            # Update bot statistics
            if hasattr(bookmark.bot, 'bookmark_count'):
                bookmark.bot.bookmark_count += 1
                db.session.commit()
            return True  # added
    
    @classmethod
    def is_bookmarked(cls, user_id: int, bot_id: int) -> bool:
        """Check if user has bookmarked this bot"""
        return cls.query.filter_by(user_id=user_id, bot_id=bot_id).first() is not None
    
    def to_dict(self):
        """Convert to dictionary for API"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bot_id": self.bot_id,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
            "bot": self.bot.to_dict() if self.bot else None
        }
    
    def __repr__(self):
        return f'<Bookmark User:{self.user_id} Bot:{self.bot_id}>'