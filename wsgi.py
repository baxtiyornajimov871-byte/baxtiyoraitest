"""
BaxtiyorAiTest - WSGI Entry Point
For production deployment with Gunicorn, uWSGI, or mod_wsgi
"""

from app import create_app

# Create the Flask application instance for WSGI server
app = create_app()

# This is required for Gunicorn and other WSGI servers
application = app

if __name__ == "__main__":
    # This block is only used when running directly (rare in production)
    app.run(host='0.0.0.0', port=5000)