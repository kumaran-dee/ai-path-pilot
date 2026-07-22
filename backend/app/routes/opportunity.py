from flask import Blueprint, jsonify

bp = Blueprint('opportunity', __name__)

@bp.route('/list', methods=['GET'])
def list_opportunities():
    return jsonify({"message": "List opportunities stub", "opportunities": []}), 200

@bp.route('/<int:id>', methods=['GET'])
def get_opportunity(id):
    return jsonify({"message": f"Opportunity details for {id} stub"}), 200

@bp.route('/<int:id>/save', methods=['POST'])
def save_opportunity(id):
    return jsonify({"message": f"Save opportunity {id} stub"}), 200

@bp.route('/<int:id>/apply', methods=['POST'])
def apply_opportunity(id):
    return jsonify({"message": f"Apply to opportunity {id} stub"}), 200
