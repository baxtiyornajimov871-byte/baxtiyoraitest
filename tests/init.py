"""
BaxtiyorAiTest - Test Suite
Unit and integration tests for the entire platform
"""

import os
import pytest
from app import create_app
from app.extensions import db

# Test configuration
@pytest.fixture(scope='session')
def app():
    """Create test application"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key-123456789',
        'SECRET_KEY': 'test-flask-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    return app

@pytest.fixture(scope='session')
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def test_db(app):
    """Setup test database"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

# Make fixtures available
__all__ = ['app', 'client', 'test_db']