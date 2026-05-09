"""
BaxtiyorAiTest - User Session Model
For tracking active sessions, secure logout, and session management
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class UserSession(BaseModel):
    """User Session Model for JWT token tracking and secure logout"""
    
    __tablename__ = 'user_sessions'
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Session Information
    session_token = Column(String(255), unique=True, nullable=False, index=True)  # JTI (JWT ID)
    refresh_token = Column(String(512), nullable=True)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 support
    device_info = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationship
    user = relationship('User', backref=db.backref('sessions', cascade="all, delete-orphan"))
    
    def __init__(self, user_id, session_token, refresh_token=None, 
                 user_agent=None, ip_address=None, device_info=None, 
                 expires_in=3600):
        self.user_id = user_id
        self.session_token = session_token
        self.refresh_token = refresh_token
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.device_info = device_info
        self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        self.is_active = True
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def revoke(self):
        """Revoke (logout) this session"""
        self.is_active = False
        db.session.commit()
    
    @classmethod
    def get_active_sessions(cls, user_id):
        """Get all active sessions for a user"""
        return cls.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(cls.expires_at > datetime.utcnow()).all()
    
    @classmethod
    def revoke_all_sessions(cls, user_id):
        """Revoke all active sessions for a user (force logout everywhere)"""
        cls.query.filter_by(user_id=user_id, is_active=True).update({
            "is_active": False
        })
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "device_info": self.device_info,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active
        }
    
    def __repr__(self):
        return f'<UserSession {self.id} for User {self.user_id} - Active: {self.is_active}>'