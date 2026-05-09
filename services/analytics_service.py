"""
BaxtiyorAiTest - Analytics Service
System analytics, usage tracking, and dashboard statistics
"""

from app.extensions import db
from app.models.analytics import AnalyticsLog
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.bot import Bot
from datetime import datetime, timedelta
from sqlalchemy import func


class AnalyticsService:
    """Analytics & Statistics Service Layer"""

    @staticmethod
    def log_event(event_type: str, **kwargs):
        """Log any analytics event"""
        log = AnalyticsLog(
            event_type=event_type,
            **kwargs
        )
        log.save()
        return log

    @staticmethod
    def get_system_dashboard_stats():
        """Get main dashboard statistics for Admin"""
        today = datetime.utcnow().date()
        last_30_days = today - timedelta(days=30)

        total_users = User.query.count()
        total_conversations = Conversation.query.count()
        total_messages = Message.query.count()
        total_bots = Bot.query.count()
        active_users_30d = User.query.filter(User.last_login >= last_30_days).count()

        # Token usage (approximate)
        total_tokens = db.session.query(func.sum(Message.total_tokens)).scalar() or 0

        return {
            "total_users": total_users,
            "active_users_30d": active_users_30d,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_bots": total_bots,
            "total_tokens_used": total_tokens,
            "storage_used_mb": 0,  # Can be calculated from uploads later
            "last_updated": datetime.utcnow().isoformat()
        }

    @staticmethod
    def get_user_analytics(user_id: int, days=30):
        """Get analytics for specific user"""
        start_date = datetime.utcnow() - timedelta(days=days)

        user_messages = Message.query.filter(
            Message.user_id == user_id,
            Message.created_at >= start_date
        ).count()

        user_conversations = Conversation.query.filter(
            Conversation.user_id == user_id,
            Conversation.created_at >= start_date
        ).count()

        return {
            "user_id": user_id,
            "messages_sent": user_messages,
            "conversations_created": user_conversations,
            "period_days": days,
            "most_used_model": "llama3-70b-8192"  # Can be calculated dynamically
        }

    @staticmethod
    def get_provider_usage_stats():
        """AI Provider usage statistics"""
        stats = db.session.query(
            Message.provider,
            func.count(Message.id).label('count'),
            func.sum(Message.total_tokens).label('tokens')
        ).group_by(Message.provider).all()

        return [
            {
                "provider": row.provider or "unknown",
                "messages": row.count,
                "tokens": row.tokens or 0
            } for row in stats
        ]

    @staticmethod
    def get_top_bots(limit=10):
        """Get most used bots"""
        return Bot.query.filter_by(is_active=True)\
                       .order_by(Bot.usage_count.desc())\
                       .limit(limit).all()

    @staticmethod
    def get_daily_active_users(days=7):
        """Daily active users for chart"""
        results = []
        for i in range(days):
            date = datetime.utcnow().date() - timedelta(days=i)
            count = User.query.filter(
                func.date(User.last_login) == date
            ).count()
            results.append({
                "date": date.isoformat(),
                "active_users": count
            })
        return results[::-1]  # Reverse to chronological order

    @staticmethod
    def get_recent_activities(limit=20):
        """Get recent system activities for admin"""
        return AnalyticsLog.query.order_by(AnalyticsLog.created_at.desc())\
                               .limit(limit).all()

    @staticmethod
    def record_chat_analytics(user_id: int, conversation_id: int, 
                            model: str, provider: str, tokens: int, 
                            duration_ms: int):
        """Record detailed chat analytics"""
        AnalyticsService.log_event(
            event_type="chat_message",
            user_id=user_id,
            conversation_id=conversation_id,
            model_name=model,
            provider=provider,
            tokens_used=tokens,
            duration_ms=duration_ms,
            description=f"Chat with {model} via {provider}"
        )