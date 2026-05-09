"""
BaxtiyorAiTest - Bot Service
Business logic for custom AI bots (Creator Ecosystem)
"""

from app.extensions import db
from app.models.bot import Bot
from app.models.like import Like
from app.models.bookmark import Bookmark
from app.models.analytics import AnalyticsLog
import uuid


class BotService:
    """Custom AI Bot Management Service"""

    @staticmethod
    def create_bot(owner_id: int, name: str, description: str, 
                   system_prompt: str, **kwargs):
        """Create a new custom AI bot"""
        if not system_prompt or len(system_prompt) < 10:
            raise ValueError("System prompt must be at least 10 characters")

        bot = Bot(
            owner_id=owner_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            category=kwargs.get('category'),
            tags=kwargs.get('tags', []),
            temperature=kwargs.get('temperature', 0.8),
            greeting_message=kwargs.get('greeting_message'),
            visibility=kwargs.get('visibility', 'public')
        )
        
        db.session.add(bot)
        db.session.commit()

        # Log analytics
        AnalyticsLog.log_event(
            event_type="bot_created",
            user_id=owner_id,
            bot_id=bot.id,
            description=f"Bot created: {name}"
        )

        return bot

    @staticmethod
    def get_bot_by_slug(slug: str):
        """Get bot by slug (public access)"""
        return Bot.query.filter_by(slug=slug, is_active=True).first()

    @staticmethod
    def get_bot_by_id(bot_id: int):
        """Get bot by ID"""
        return Bot.query.get(bot_id)

    @staticmethod
    def get_user_bots(owner_id: int):
        """Get all bots created by a user"""
        return Bot.query.filter_by(owner_id=owner_id, is_active=True)\
                       .order_by(Bot.created_at.desc()).all()

    @staticmethod
    def update_bot(bot_id: int, owner_id: int, data: dict):
        """Update existing bot (owner only)"""
        bot = Bot.query.get(bot_id)
        if not bot or bot.owner_id != owner_id:
            raise ValueError("Bot not found or access denied")

        if 'name' in data:
            bot.name = data['name']
        if 'description' in data:
            bot.description = data['description']
        if 'system_prompt' in data:
            bot.system_prompt = data['system_prompt']
        if 'temperature' in data:
            bot.temperature = data['temperature']
        if 'greeting_message' in data:
            bot.greeting_message = data['greeting_message']
        if 'category' in data:
            bot.category = data['category']
        if 'tags' in data:
            bot.tags = data['tags']
        if 'visibility' in data:
            bot.visibility = data['visibility']

        db.session.commit()
        return bot

    @staticmethod
    def delete_bot(bot_id: int, owner_id: int):
        """Delete bot (owner only)"""
        bot = Bot.query.get(bot_id)
        if not bot or bot.owner_id != owner_id:
            raise ValueError("Bot not found or access denied")
        
        bot.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def search_bots(query: str = None, category: str = None, limit=20):
        """Search public bots"""
        q = Bot.query.filter_by(is_active=True, visibility='public')
        
        if query:
            q = q.filter(
                db.or_(
                    Bot.name.ilike(f"%{query}%"),
                    Bot.description.ilike(f"%{query}%")
                )
            )
        
        if category:
            q = q.filter_by(category=category)
            
        return q.order_by(Bot.usage_count.desc(), Bot.likes_count.desc())\
                .limit(limit).all()

    @staticmethod
    def get_trending_bots(limit=10):
        """Get trending bots"""
        return Bot.query.filter_by(is_active=True, visibility='public')\
                       .order_by(Bot.usage_count.desc(), Bot.likes_count.desc())\
                       .limit(limit).all()

    @staticmethod
    def get_featured_bots(limit=8):
        """Get featured / verified bots"""
        return Bot.query.filter_by(is_active=True, is_verified=True)\
                       .order_by(Bot.likes_count.desc()).limit(limit).all()

    @staticmethod
    def increment_usage(bot_id: int):
        """Increment bot usage count"""
        bot = Bot.query.get(bot_id)
        if bot:
            bot.increment_usage()
            return True
        return False

    @staticmethod
    def toggle_like(user_id: int, bot_id: int):
        """Like / Unlike bot"""
        return Like.toggle_like(user_id, bot_id)

    @staticmethod
    def toggle_bookmark(user_id: int, bot_id: int, note: str = None):
        """Bookmark / Remove bookmark"""
        return Bookmark.toggle_bookmark(user_id, bot_id, note)

    @staticmethod
    def get_bot_with_stats(bot_id: int):
        """Get bot with like & bookmark status (for authenticated users)"""
        bot = Bot.query.get(bot_id)
        if not bot:
            return None
        return bot.to_dict(include_owner=True)