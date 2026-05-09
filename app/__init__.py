"""
BaxtiyorAiTest - Application Factory
"""

from flask import Flask
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

from .config import Config
from .extensions import db, jwt, migrate, limiter


def create_app(config_class=Config):
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static',
                static_url_path='/static')

    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # BLUEPRINTLARNI YOQISH
    try:
        from .routes.init import register_blueprints
        register_blueprints(app)
        print("✅ All blueprints registered successfully")
    except Exception as e:
        print(f"❌ Blueprint error: {e}")
        import traceback
        traceback.print_exc()

    # Logging
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        file_handler = RotatingFileHandler('logs/baxtiyoraI.log', maxBytes=10*1024*1024, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    for d in ['uploads', 'logs', 'backups', 'instance']:
        os.makedirs(d, exist_ok=True)

    app.logger.info('🚀 BaxtiyorAiTest Application initialized successfully')

    return app