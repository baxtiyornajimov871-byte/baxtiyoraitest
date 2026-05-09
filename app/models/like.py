"""
BaxtiyorAiTest - Like Model
For liking custom bots and future content
"""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class Like(BaseModel):
    """Like Model - User likes on bots (and future content)"""
    
    __tablename__ = 'likes'
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    bot_id = Column(Integer, ForeignKey('bots.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Relationships
    user = relationship('User', back_populates='likes')
    bot = relationship('Bot', back_populates='likes')
    
    # Unique constraint: one user can like a bot only once
    __table_args__ = (
        UniqueConstraint('user_id', 'bot_id', name='uq_user_bot_like'),
    )
    
    def __init__(self, user_id: int, bot_id: int):
        self.user_id = user_id
        self.bot_id = bot_id
    
    @classmethod
    def toggle_like(cls, user_id: int, bot_id: int):
        """Toggle like (like if not liked, unlike if already liked)"""
        existing = cls.query.filter_by(user_id=user_id, bot_id=bot_id).first()
        
        if existing:
            # Unlike
            existing.delete()
            if hasattr(existing.bot, 'decrement_likes'):
                existing.bot.decrement_likes()
            return False  # unliked
        else:
            # Like
            like = cls(user_id=user_id, bot_id=bot_id)
            like.save()
            if hasattr(like.bot, 'increment_likes'):
                like.bot.increment_likes()
            return True  # liked
    
    @classmethod
    def is_liked(cls, user_id: int, bot_id: int) -> bool:
        """Check if user already liked this bot"""
        return cls.query.filter_by(user_id=user_id, bot_id=bot_id).first() is not None
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bot_id": self.bot_id,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Like User:{self.user_id} Bot:{self.bot_id}>'