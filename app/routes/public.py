"""
BaxtiyorAiTest - Public Routes
No authentication required - Public marketplace, discovery, and info endpoints
"""

from flask import request, jsonify, render_template
from app.routes import public_bp
from app.services.bot_service import BotService
from app.services.creator_service import CreatorService
from app.services.ai_service import AIService


@public_bp.route('/', methods=['GET'])
def home():
    """Main landing page"""
    return render_template('index.html')


@public_bp.route('/bots', methods=['GET'])
def public_bots():
    """Public Bot Marketplace"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 30))
        
        bots = BotService.search_bots(
            query=query if query else None,
            category=category,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "bots": [bot.to_dict(include_owner=True) for bot in bots],
            "total": len(bots),
            "query": query
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/bots/trending', methods=['GET'])
def trending_bots():
    """Trending bots endpoint"""
    try:
        limit = int(request.args.get('limit', 15))
        bots = BotService.get_trending_bots(limit=limit)
        
        return jsonify({
            "success": True,
            "bots": [bot.to_dict(include_owner=True) for bot in bots]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/bots/featured', methods=['GET'])
def featured_bots():
    """Featured bots"""
    try:
        limit = int(request.args.get('limit', 12))
        bots = BotService.get_featured_bots(limit=limit)
        
        return jsonify({
            "success": True,
            "bots": [bot.to_dict(include_owner=True) for bot in bots]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/creators', methods=['GET'])
def public_creators():
    """Public Creators List"""
    try:
        limit = int(request.args.get('limit', 20))
        creators = CreatorService.get_featured_creators(limit=limit)
        
        return jsonify({
            "success": True,
            "creators": [c.to_dict() for c in creators]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/creator/<string:username>', methods=['GET'])
def public_creator_profile(username):
    """Public Creator Profile"""
    try:
        profile = CreatorService.get_public_creator_profile(username)
        if not profile:
            return jsonify({"success": False, "error": "Creator not found"}), 404
        
        return jsonify({
            "success": True,
            "profile": profile
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/bots/<string:slug>', methods=['GET'])
def public_bot_detail(slug):
    """Single Bot Detail Page"""
    try:
        bot = BotService.get_bot_by_slug(slug)
        if not bot:
            return jsonify({"success": False, "error": "Bot not found"}), 404
        
        return jsonify({
            "success": True,
            "bot": bot.to_dict(include_owner=True)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@public_bp.route('/models', methods=['GET'])
def available_models():
    """List all available AI models"""
    try:
        models = AIService.get_available_models()
        return jsonify({
            "success": True,
            "models": models
        }), 200
    except Exception:
        return jsonify({
            "success": True,
            "models": {
                "groq": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
                "huggingface": ["mistralai/Mistral-7B-Instruct-v0.2"]
            }
        }), 200


@public_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for monitoring, Docker, etc."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "app": "BaxtiyorAiTest",
        "version": "1.0.0",
        "message": "Platform is running smoothly"
    }), 200