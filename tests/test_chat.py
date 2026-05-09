"""
BaxtiyorAiTest - Chat System Tests
Unit and integration tests for conversations and messaging
"""

import pytest
from app.services.chat_service import ChatService
from app.services.auth_service import AuthService
from app.models.conversation import Conversation
from app.models.message import Message


def test_create_conversation(client, test_db):
    """Test creating a new conversation"""
    # Create test user
    user = AuthService.register_user("chatuser", "chat@example.com", "StrongPass123")
    
    conversation = ChatService.create_conversation(
        user_id=user.id,
        title="Test Conversation",
        model="llama3-70b-8192"
    )
    
    assert conversation is not None
    assert conversation.title == "Test Conversation"
    assert conversation.user_id == user.id
    assert conversation.message_count == 0


def test_add_message(client, test_db):
    """Test adding messages to conversation"""
    user = AuthService.register_user("msguser", "msg@example.com", "StrongPass123")
    conv = ChatService.create_conversation(user.id, "Message Test")
    
    # Add user message
    user_msg = ChatService.add_message(
        conversation_id=conv.id,
        role="user",
        content="Salom, qalaysiz?",
        user_id=user.id
    )
    
    # Add assistant message
    ai_msg = ChatService.add_message(
        conversation_id=conv.id,
        role="assistant",
        content="Salom! Yaxshiman, rahmat. Sizga qanday yordam bera olaman?",
        model="llama3-70b-8192",
        provider="groq"
    )
    
    assert user_msg.role == "user"
    assert ai_msg.role == "assistant"
    assert conv.message_count == 2


def test_get_user_conversations(client, test_db):
    """Test retrieving user's conversations"""
    user = AuthService.register_user("listuser", "list@example.com", "StrongPass123")
    
    # Create multiple conversations
    ChatService.create_conversation(user.id, "First Chat")
    ChatService.create_conversation(user.id, "Second Chat")
    
    conversations = ChatService.get_user_conversations(user.id)
    
    assert len(conversations) == 2
    assert conversations[0].title == "Second Chat"  # Latest first


def test_pin_and_favorite(client, test_db):
    """Test pin and favorite functionality"""
    user = AuthService.register_user("pinuser", "pin@example.com", "StrongPass123")
    conv = ChatService.create_conversation(user.id, "Pin Test")
    
    # Pin
    ChatService.toggle_pin(conv.id, user.id)
    assert conv.is_pinned is True
    
    # Favorite
    ChatService.toggle_favorite(conv.id, user.id)
    assert conv.is_favorite is True


def test_search_conversations(client, test_db):
    """Test conversation search"""
    user = AuthService.register_user("searchuser", "search@example.com", "StrongPass123")
    ChatService.create_conversation(user.id, "Python dasturlash haqida")
    ChatService.create_conversation(user.id, "AI kelajagi")
    
    results = ChatService.search_conversations(user.id, "Python")
    
    assert len(results) == 1
    assert "Python" in results[0].title


def test_delete_conversation(client, test_db):
    """Test soft delete conversation"""
    user = AuthService.register_user("deluser", "del@example.com", "StrongPass123")
    conv = ChatService.create_conversation(user.id, "To be deleted")
    
    success = ChatService.delete_conversation(conv.id, user.id)
    assert success is True
    
    # Should not appear in normal list
    conversations = ChatService.get_user_conversations(user.id)
    assert len(conversations) == 0