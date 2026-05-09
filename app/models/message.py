"""
BaxtiyorAiTest - Message Model
Stores all chat messages with full metadata and AI response tracking
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel
from app.extensions import db


class Message(BaseModel):
    """Message Model - Individual chat messages"""
    
    __tablename__ = 'messages'
    
    # Foreign Keys
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Message Content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # AI Metadata
    model = Column(String(100), nullable=True)          # e.g., "llama3-70b-8192"
    provider = Column(String(50), nullable=True)        # "groq", "huggingface", "fallback"
    temperature = Column(Float, default=0.7)
    
    # Token usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Status & Features
    is_edited = Column(Boolean, default=False)
    is_regenerated = Column(Boolean, default=False)
    is_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Additional Data (for future features)
    metadata = Column(JSON, nullable=True)  # For storing images, file references, etc.
    
    # Relationships
    conversation = relationship('Conversation', back_populates='messages')
    user = relationship('User', back_populates='messages')
    
    def __init__(self, conversation_id, role, content, 
                 model=None, provider=None, temperature=0.7, 
                 user_id=None, **kwargs):
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.user_id = user_id
        self.metadata = kwargs.get('metadata', {})
    
    def mark_as_regenerated(self):
        """Mark message as regenerated"""
        self.is_regenerated = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_error(self, error_msg: str):
        """Mark message as error"""
        self.is_error = True
        self.error_message = error_msg
        self.save()
    
    def add_token_usage(self, prompt_tokens: int, completion_tokens: int):
        """Update token usage statistics"""
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens
        self.save()
    
    def to_dict(self):
        """Convert message to API-friendly dictionary"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "temperature": self.temperature,
            "is_edited": self.is_edited,
            "is_regenerated": self.is_regenerated,
            "is_error": self.is_error,
            "error_message": self.error_message,
            "total_tokens": self.total_tokens,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {}
        }
    
    def __repr__(self):
        return f'<Message {self.id} | {self.role} in Conv {self.conversation_id}>'