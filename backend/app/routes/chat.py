from flask import Blueprint, jsonify, request

bp = Blueprint('chat', __name__)

@bp.route('/message', methods=['POST'])
def chat_message():
    return jsonify({"message": "AI Career Chat message stub"}), 200
