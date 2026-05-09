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

    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # === Vaqtincha blueprintlar o‘chirildi ===
    # from .routes import register_blueprints
    # register_blueprints(app)

    # Logging
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler(
            'logs/baxtiyoraI.log', 
            maxBytes=10*1024*1024, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Create required directories
    for d in ['uploads', 'logs', 'backups', 'instance']:
        os.makedirs(d, exist_ok=True)

    app.logger.info('🚀 BaxtiyorAiTest Application initialized successfully')

    # Temporary Home Route
    @app.route('/')
    def home():
        return """
        <h1>🚀 BaxtiyorAiTest</h1>
        <p><strong>Platforma muvaffaqiyatli ishga tushdi!</strong></p>
        <p><a href="/login">Login sahifasi</a> | <a href="/register">Register sahifasi</a></p>
        <hr>
        <small>Debug mode: Development</small>
        """

    return app