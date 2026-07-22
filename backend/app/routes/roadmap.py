from flask import Blueprint, jsonify

bp = Blueprint('roadmap', __name__)

@bp.route('/generate', methods=['GET'])
def generate_roadmap():
    return jsonify({"message": "Career roadmap generation stub"}), 200
