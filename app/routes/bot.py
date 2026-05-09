"""
BaxtiyorAiTest - Bot Routes
Custom AI Bot management and marketplace endpoints
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes import bot_bp
from app.services.bot_service import BotService


@bot_bp.route('/', methods=['POST'])
@jwt_required()
def create_bot():
    """Create a new custom AI bot"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required = ['name', 'description', 'system_prompt']
        if not all(k in data for k in required):
            return jsonify({"error": "Name, description and system prompt are required"}), 400

        bot = BotService.create_bot(
            owner_id=user_id,
            name=data['name'],
            description=data['description'],
            system_prompt=data['system_prompt'],
            category=data.get('category'),
            tags=data.get('tags', []),
            temperature=data.get('temperature', 0.8),
            greeting_message=data.get('greeting_message'),
            visibility=data.get('visibility', 'public')
        )

        return jsonify({
            "message": "Bot created successfully",
            "bot": bot.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to create bot"}), 500


@bot_bp.route('/', methods=['GET'])
def get_bots():
    """Get public bots (marketplace)"""
    try:
        query = request.args.get('q')
        category = request.args.get('category')
        
        if query or category:
            bots = BotService.search_bots(query=query, category=category)
        else:
            bots = BotService.get_trending_bots(limit=30)
        
        return jsonify({
            "bots": [bot.to_dict(include_owner=True) for bot in bots]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bot_bp.route('/featured', methods=['GET'])
def get_featured_bots():
    """Get featured bots"""
    try:
        bots = BotService.get_featured_bots(limit=12)
        return jsonify({
            "bots": [bot.to_dict(include_owner=True) for bot in bots]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bot_bp.route('/<string:slug>', methods=['GET'])
def get_bot(slug):
    """Get single bot by slug (public)"""
    try:
        bot = BotService.get_bot_by_slug(slug)
        if not bot:
            return jsonify({"error": "Bot not found"}), 404
        
        return jsonify(bot.to_dict(include_owner=True)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bot_bp.route('/<int:bot_id>', methods=['PUT'])
@jwt_required()
def update_bot(bot_id):
    """Update own bot"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        bot = BotService.update_bot(bot_id, user_id, data)
        
        return jsonify({
            "message": "Bot updated successfully",
            "bot": bot.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update bot"}), 500


@bot_bp.route('/<int:bot_id>', methods=['DELETE'])
@jwt_required()
def delete_bot(bot_id):
    """Delete own bot"""
    try:
        user_id = get_jwt_identity()
        BotService.delete_bot(bot_id, user_id)
        
        return jsonify({"message": "Bot deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to delete bot"}), 500


@bot_bp.route('/<int:bot_id>/like', methods=['POST'])
@jwt_required()
def like_bot(bot_id):
    """Like / Unlike bot"""
    try:
        user_id = get_jwt_identity()
        liked = BotService.toggle_like(user_id, bot_id)
        
        return jsonify({
            "message": "Like updated",
            "liked": liked
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bot_bp.route('/<int:bot_id>/bookmark', methods=['POST'])
@jwt_required()
def bookmark_bot(bot_id):
    """Bookmark / Remove bookmark"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        bookmarked = BotService.toggle_bookmark(user_id, bot_id, data.get('note'))
        
        return jsonify({
            "message": "Bookmark updated",
            "bookmarked": bookmarked
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bot_bp.route('/my-bots', methods=['GET'])
@jwt_required()
def get_my_bots():
    """Get all bots created by current user"""
    try:
        user_id = get_jwt_identity()
        bots = BotService.get_user_bots(user_id)
        
        return jsonify({
            "bots": [bot.to_dict() for bot in bots]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500