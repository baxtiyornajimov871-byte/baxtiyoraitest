"""
BaxtiyorAiTest - Creator Profile Model
Extended profile for users who become creators
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel
from app.extensions import db


class CreatorProfile(BaseModel):
    """Creator Profile - Extended information for creators"""
    
    __tablename__ = 'creator_profiles'
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), 
                    nullable=False, unique=True, index=True)
    
    # Creator Branding
    banner_image = Column(String(255), nullable=True)
    tagline = Column(String(200), nullable=True)
    featured_bot_id = Column(Integer, ForeignKey('bots.id'), nullable=True)
    
    # Statistics
    total_bots = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    total_usage = Column(Integer, default=0)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verification_reason = Column(Text, nullable=True)
    
    # Social & Links (additional to User model)
    twitter_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    tiktok_url = Column(String(255), nullable=True)
    
    # About
    about_me = Column(Text, nullable=True)
    expertise = Column(Text, nullable=True)  # e.g., "AI, Programming, Creative Writing"
    
    # Relationships
    user = relationship('User', back_populates='creator_profile')
    featured_bot = relationship('Bot')
    
    def increment_stats(self, likes=0, usage=0):
        """Update creator statistics"""
        if likes:
            self.total_likes += likes
        if usage:
            self.total_usage += usage
        db.session.commit()
    
    def verify_creator(self, reason: str = None):
        """Verify creator account"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        if reason:
            self.verification_reason = reason
        db.session.commit()
    
    def to_dict(self):
        """Public profile data"""
        return {
            "user_id": self.user_id,
            "username": self.user.username,
            "display_name": self.user.display_name,
            "avatar": self.user.avatar,
            "banner_image": self.banner_image,
            "tagline": self.tagline,
            "about_me": self.about_me,
            "expertise": self.expertise,
            "total_bots": self.total_bots,
            "total_likes": self.total_likes,
            "total_followers": self.total_followers,
            "total_usage": self.total_usage,
            "is_verified": self.is_verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "social_links": {
                "website": self.user.website,
                "github": self.user.github_url,
                "youtube": self.user.youtube_url,
                "instagram": self.user.instagram_url,
                "twitter": self.twitter_url,
                "linkedin": self.linkedin_url
            },
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CreatorProfile {self.user.username} - Verified: {self.is_verified}>'