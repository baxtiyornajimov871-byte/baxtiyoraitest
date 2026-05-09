"""
BaxtiyorAiTest - Analytics Model
System-wide and per-user analytics logging for dashboard and insights
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel
from app.extensions import db


class AnalyticsLog(BaseModel):
    """Analytics Logging Model"""
    
    __tablename__ = 'analytics_logs'
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    bot_id = Column(Integer, ForeignKey('bots.id', ondelete='SET NULL'), nullable=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True)
    
    # Event Information
    event_type = Column(String(50), nullable=False, index=True)  # e.g., "chat_message", "bot_created", "login", "upload"
    event_category = Column(String(50), nullable=True)  # "user", "ai", "system", "creator"
    
    # Details
    description = Column(String(255), nullable=True)
    metadata = Column(JSON, nullable=True)  # Flexible data storage
    
    # Performance & Usage
    duration_ms = Column(Integer, nullable=True)        # Response time
    tokens_used = Column(Integer, nullable=True)
    provider = Column(String(50), nullable=True)        # groq, huggingface, etc.
    model_name = Column(String(100), nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship('User')
    bot = relationship('Bot')
    conversation = relationship('Conversation')
    
    def __init__(self, event_type: str, user_id=None, bot_id=None, 
                 conversation_id=None, description=None, metadata=None, 
                 duration_ms=None, tokens_used=None, provider=None, model_name=None):
        self.event_type = event_type
        self.user_id = user_id
        self.bot_id = bot_id
        self.conversation_id = conversation_id
        self.description = description
        self.metadata = metadata or {}
        self.duration_ms = duration_ms
        self.tokens_used = tokens_used
        self.provider = provider
        self.model_name = model_name
    
    @classmethod
    def log_event(cls, event_type: str, **kwargs):
        """Quick way to log analytics"""
        log = cls(event_type=event_type, **kwargs)
        log.save()
        return log
    
    @classmethod
    def get_daily_stats(cls, days=30):
        """Get aggregated statistics (for admin dashboard)"""
        # This would typically use more complex queries with SQLAlchemy
        pass
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_category": self.event_category,
            "description": self.description,
            "user_id": self.user_id,
            "bot_id": self.bot_id,
            "conversation_id": self.conversation_id,
            "tokens_used": self.tokens_used,
            "duration_ms": self.duration_ms,
            "provider": self.provider,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    def __repr__(self):
        return f'<AnalyticsLog {self.event_type} at {self.created_at}>'