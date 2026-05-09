"""
BaxtiyorAiTest - Creator Service
Business logic for creator profiles and creator ecosystem
"""

from app.extensions import db
from app.models.creator import CreatorProfile
from app.models.user import User
from app.models.bot import Bot


class CreatorService:
    """Creator Profile & Dashboard Service Layer"""

    @staticmethod
    def get_creator_profile(user_id: int):
        """Get creator profile by user ID"""
        profile = CreatorProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            # Auto-create if user is creator
            user = User.query.get(user_id)
            if user and user.role == 'creator':
                profile = CreatorProfile(user_id=user_id)
                db.session.add(profile)
                db.session.commit()
        return profile

    @staticmethod
    def update_creator_profile(user_id: int, data: dict):
        """Update creator profile information"""
        profile = CreatorService.get_creator_profile(user_id)
        if not profile:
            raise ValueError("Creator profile not found")

        # Update CreatorProfile fields
        if 'tagline' in data:
            profile.tagline = data['tagline']
        if 'about_me' in data:
            profile.about_me = data['about_me']
        if 'expertise' in data:
            profile.expertise = data['expertise']
        if 'banner_image' in data:
            profile.banner_image = data['banner_image']

        # Update linked User fields
        user = profile.user
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'bio' in data:
            user.bio = data['bio']

        db.session.commit()
        return profile.to_dict()

    @staticmethod
    def get_public_creator_profile(username: str):
        """Get public creator profile (for /creator/<username> page)"""
        user = User.query.filter_by(username=username).first()
        if not user or user.role != 'creator':
            return None

        profile = CreatorService.get_creator_profile(user.id)
        if not profile:
            return None

        data = profile.to_dict()
        # Add creator's public bots
        data['bots'] = [bot.to_dict() for bot in 
                       Bot.query.filter_by(owner_id=user.id, is_active=True, visibility='public')
                       .order_by(Bot.likes_count.desc()).limit(12).all()]
        
        return data

    @staticmethod
    def get_creator_dashboard(user_id: int):
        """Get full data for creator dashboard"""
        profile = CreatorService.get_creator_profile(user_id)
        if not profile:
            raise ValueError("Not a creator")

        bots = Bot.query.filter_by(owner_id=user_id, is_active=True)\
                       .order_by(Bot.created_at.desc()).all()

        total_usage = sum(bot.usage_count for bot in bots)
        total_likes = sum(bot.likes_count for bot in bots)

        profile.total_bots = len(bots)
        profile.total_usage = total_usage
        profile.total_likes = total_likes
        db.session.commit()

        return {
            "profile": profile.to_dict(),
            "bots": [bot.to_dict() for bot in bots],
            "stats": {
                "total_bots": len(bots),
                "total_usage": total_usage,
                "total_likes": total_likes,
                "total_followers": profile.total_followers
            }
        }

    @staticmethod
    def get_featured_creators(limit=10):
        """Get featured creators for marketplace"""
        return CreatorProfile.query.filter_by(is_verified=True)\
                                  .order_by(CreatorProfile.total_likes.desc())\
                                  .limit(limit).all()

    @staticmethod
    def verify_creator(user_id: int, admin_id: int, reason: str = None):
        """Admin: Verify creator"""
        profile = CreatorService.get_creator_profile(user_id)
        if not profile:
            raise ValueError("Creator profile not found")
        
        profile.verify_creator(reason)
        
        # Log analytics
        from .analytics_service import AnalyticsService
        AnalyticsService.log_event(
            event_type="creator_verified",
            user_id=user_id,
            description=f"Verified by admin {admin_id}"
        )
        return True

    @staticmethod
    def get_all_creators_paginated(page=1, per_page=20):
        """Admin: Get all creators with pagination"""
        return CreatorProfile.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )