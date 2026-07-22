from flask import Blueprint, jsonify

bp = Blueprint('notifications', __name__)

@bp.route('/list', methods=['GET'])
def list_notifications():
    return jsonify({"message": "List notifications stub", "notifications": []}), 200
