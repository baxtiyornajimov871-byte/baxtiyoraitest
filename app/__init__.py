"""
BaxtiyorAiTest - Application Factory
Production-ready Flask Application Initialization
"""

from flask import Flask
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

from .config import Config
from .extensions import db, jwt, migrate, limiter


def create_app(config_class=Config):
    """Create and configure the Flask application"""
    
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static',
                static_url_path='/static')

    # Load configuration
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # === BLUEPRINTS VA ERROR HANDLERLarni vaqtincha o‘chirib turamiz ===
    # from .routes import register_blueprints
    # register_blueprints(app)

    # from .middleware.error_handler import register_error_handlers
    # register_error_handlers(app)

    # Logging
    if not app.debug and not app.testing:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler('logs/baxtiyoraI.log', maxBytes=10*1024*1024, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Create directories
    for directory in ['uploads', 'logs', 'backups', 'instance']:
        os.makedirs(directory, exist_ok=True)

    app.logger.info('🚀 BaxtiyorAiTest Application initialized successfully')
    return app