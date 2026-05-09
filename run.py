"""
BaxtiyorAiTest - Main Entry Point
Production-ready Flask application launcher
"""

from app import create_app
import os

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 BaxtiyorAiTest starting on http://0.0.0.0:{port}")
    print(f"🌍 Environment: {'Development' if debug else 'Production'}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )