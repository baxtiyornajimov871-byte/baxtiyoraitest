"""
BaxtiyorAiTest - Upload Model
Secure file upload management with metadata and usage tracking
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .base import BaseModel
from app.extensions import db


class Upload(BaseModel):
    """File Upload Model - Supports images, PDF, documents, etc."""
    
    __tablename__ = 'uploads'
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # File Information
    original_filename = Column(String(255), nullable=False)
    secure_filename = Column(String(255), unique=True, nullable=False)  # UUID-based
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(100), nullable=False)  # mime type
    file_extension = Column(String(10), nullable=True)
    
    # Content & Processing
    extracted_text = Column(Text, nullable=True)  # For PDF, DOCX, TXT
    preview_url = Column(String(255), nullable=True)  # For images
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    
    # Usage Metadata
    metadata = Column(JSON, nullable=True)  # width, height, page_count, duration, etc.
    used_in_conversations = Column(Integer, default=0)
    
    # Relationships
    user = relationship('User', back_populates='uploads')
    conversation = relationship('Conversation')
    
    def __init__(self, user_id, original_filename, file_path, file_size, 
                 file_type, conversation_id=None):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.original_filename = original_filename
        self.secure_filename = f"{uuid.uuid4().hex}_{original_filename}"
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
        self.file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else None
    
    def mark_as_processed(self, extracted_text: str = None, preview_url: str = None):
        """Mark file as successfully processed"""
        self.is_processed = True
        if extracted_text:
            self.extracted_text = extracted_text[:50000]  # Limit size
        if preview_url:
            self.preview_url = preview_url
        self.save()
    
    def mark_as_failed(self, error: str):
        """Mark processing as failed"""
        self.processing_error = error
        self.save()
    
    def increment_usage(self):
        """Track how many times this file was used in chats"""
        self.used_in_conversations += 1
        db.session.commit()
    
    def soft_delete(self):
        """Soft delete the upload record"""
        self.is_deleted = True
        self.save()
    
    def get_size_readable(self) -> str:
        """Return human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def to_dict(self):
        """Convert to API response format"""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "secure_filename": self.secure_filename,
            "file_size": self.file_size,
            "readable_size": self.get_size_readable(),
            "file_type": self.file_type,
            "file_extension": self.file_extension,
            "preview_url": self.preview_url,
            "is_processed": self.is_processed,
            "extracted_text_preview": self.extracted_text[:200] if self.extracted_text else None,
            "used_in_conversations": self.used_in_conversations,
            "created_at": self.created_at.isoformat(),
            "conversation_id": self.conversation_id
        }
    
    def __repr__(self):
        return f'<Upload {self.id}: {self.original_filename} ({self.get_size_readable()})>'