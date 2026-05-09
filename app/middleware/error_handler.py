"""
BaxtiyorAiTest - Global Error Handler Middleware
Centralized exception handling and user-friendly error responses
"""

from flask import jsonify, request
import logging
import traceback


def register_error_handlers(app):
    """Register global error handlers for the Flask app"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "Invalid request"
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication required. Please login."
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "error": "Forbidden",
            "message": "You don't have permission to access this resource."
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": f"The requested resource {request.path} was not found.",
            "path": request.path
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "error": "File Too Large",
            "message": "The uploaded file exceeds the maximum allowed size (50MB)."
        }), 413

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            "error": "Too Many Requests",
            "message": "You have exceeded the rate limit. Please try again later."
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        # Log the full traceback in production
        app.logger.error(f"Server Error: {traceback.format_exc()}")
        
        return jsonify({
            "error": "Internal Server Error",
            "message": "Something went wrong on our end. Our team has been notified."
        }), 500

    # Custom exception handler
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f"Unexpected Error: {str(error)}\n{traceback.format_exc()}")
        
        return jsonify({
            "error": "Unexpected Error",
            "message": "An unexpected error occurred. Please try again later."
        }), 500


# Custom exception classes
class BaxtiyorAPIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(BaxtiyorAPIException):
    """Validation error"""
    def __init__(self, message="Invalid input data"):
        super().__init__(message, 400)


class ResourceNotFoundError(BaxtiyorAPIException):
    """Resource not found"""
    def __init__(self, resource="Resource"):
        super().__init__(f"{resource} not found", 404)