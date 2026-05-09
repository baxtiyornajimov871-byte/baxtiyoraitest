"""
BaxtiyorAiTest - Chat Service
Core business logic for conversations and message management
"""

from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.upload import Upload
from datetime import datetime


class ChatService:
    """Chat & Conversation Business Logic Layer"""

    @staticmethod
    def create_conversation(user_id: int, title: str = "New Chat", model: str = "llama3-70b-8192"):
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            model_used=model
        )
        conversation.save()
        return conversation

    @staticmethod
    def get_user_conversations(user_id: int, include_archived=False, limit=50):
        """Get all conversations for a user"""
        query = Conversation.query.filter_by(user_id=user_id, is_deleted=False)
        
        if not include_archived:
            query = query.filter_by(is_archived=False)
            
        return query.order_by(Conversation.is_pinned.desc(), 
                            Conversation.last_message_at.desc()).limit(limit).all()

    @staticmethod
    def get_conversation_by_id(conversation_id: int, user_id: int = None):
        """Get single conversation with permission check"""
        conv = Conversation.query.get(conversation_id)
        if not conv:
            return None
        if user_id and conv.user_id != user_id:
            return None  # Permission denied
        return conv

    @staticmethod
    def update_conversation_title(conversation_id: int, new_title: str, user_id: int):
        """Update conversation title"""
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found or access denied")
        
        conv.update_title(new_title)
        return conv

    @staticmethod
    def delete_conversation(conversation_id: int, user_id: int):
        """Soft delete conversation"""
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        conv.soft_delete()
        return True

    @staticmethod
    def toggle_pin(conversation_id: int, user_id: int):
        """Pin/Unpin conversation"""
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        conv.toggle_pin()
        return conv.is_pinned

    @staticmethod
    def toggle_favorite(conversation_id: int, user_id: int):
        """Add/Remove from favorites"""
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        conv.toggle_favorite()
        return conv.is_favorite

    @staticmethod
    def archive_conversation(conversation_id: int, user_id: int):
        """Archive conversation"""
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        conv.archive()
        return True

    @staticmethod
    def add_message(conversation_id: int, role: str, content: str, 
                   model: str = None, provider: str = None, 
                   user_id: int = None, temperature: float = 0.7):
        """Add a new message to conversation"""
        conv = Conversation.query.get(conversation_id)
        if not conv or (user_id and conv.user_id != user_id):
            raise ValueError("Conversation not found or access denied")

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            provider=provider,
            temperature=temperature,
            user_id=user_id if role == "user" else None
        )
        message.save()
        
        # Update conversation stats
        conv.increment_message_count()
        
        return message

    @staticmethod
    def get_conversation_messages(conversation_id: int, user_id: int, limit=100):
        """Get messages for a conversation"""
        conv = ChatService.get_conversation_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found")
        
        return Message.query.filter_by(conversation_id=conversation_id)\
                          .order_by(Message.created_at.asc())\
                          .limit(limit).all()

    @staticmethod
    def get_recent_messages(conversation_id: int, limit=10):
        """Get last N messages for context (AI memory)"""
        return Message.query.filter_by(conversation_id=conversation_id)\
                          .order_by(Message.created_at.desc())\
                          .limit(limit).all()

    @staticmethod
    def search_conversations(user_id: int, query: str):
        """Search conversations by title"""
        return Conversation.query.filter(
            Conversation.user_id == user_id,
            Conversation.is_deleted == False,
            Conversation.title.ilike(f"%{query}%")
        ).order_by(Conversation.updated_at.desc()).all()