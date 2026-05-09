"""
BaxtiyorAiTest - Authentication Tests
Unit tests for registration, login, JWT, and auth flows
"""

import pytest
import json
from app.models.user import User
from app.services.auth_service import AuthService


def test_register_user(client, test_db):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongPass123",
        "display_name": "Test User"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == "User registered successfully"
    assert 'user' in data


def test_register_duplicate_username(client, test_db):
    """Test duplicate username prevention"""
    # First user
    client.post('/api/auth/register', json={
        "username": "duplicate",
        "email": "first@example.com",
        "password": "StrongPass123"
    })
    
    # Second user with same username
    response = client.post('/api/auth/register', json={
        "username": "duplicate",
        "email": "second@example.com",
        "password": "StrongPass123"
    })
    
    assert response.status_code == 400
    assert "Username already taken" in response.get_json()['error']


def test_login_success(client, test_db):
    """Test successful login"""
    # Create user
    AuthService.register_user("loginuser", "login@example.com", "StrongPass123")
    
    response = client.post('/api/auth/login', json={
        "email": "login@example.com",
        "password": "StrongPass123"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


def test_login_invalid_credentials(client, test_db):
    """Test login with wrong password"""
    AuthService.register_user("wrongpass", "wrong@example.com", "CorrectPass123")
    
    response = client.post('/api/auth/login', json={
        "email": "wrong@example.com",
        "password": "WrongPass123"
    })
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.get_json()['error']


def test_protected_route_without_token(client):
    """Test accessing protected route without JWT"""
    response = client.get('/api/auth/me')
    assert response.status_code == 401


def test_protected_route_with_token(client, test_db):
    """Test protected route with valid JWT"""
    # Register and login
    AuthService.register_user("tokenuser", "token@example.com", "StrongPass123")
    login_resp = client.post('/api/auth/login', json={
        "email": "token@example.com",
        "password": "StrongPass123"
    })
    
    token = login_resp.get_json()['access_token']
    
    # Access protected route
    response = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == "tokenuser"


def test_logout(client, test_db):
    """Test logout functionality"""
    # Register and login
    AuthService.register_user("logoutuser", "logout@example.com", "StrongPass123")
    login_resp = client.post('/api/auth/login', json={
        "email": "logout@example.com",
        "password": "StrongPass123"
    })
    
    token = login_resp.get_json()['access_token']
    
    response = client.post('/api/auth/logout', headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200