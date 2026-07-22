from flask import Blueprint, jsonify

bp = Blueprint('dashboard', __name__)

@bp.route('/summary', methods=['GET'])
def get_summary():
    return jsonify({"message": "Dashboard summary stub"}), 200
