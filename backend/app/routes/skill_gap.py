from flask import Blueprint, jsonify

bp = Blueprint('skill_gap', __name__)

@bp.route('/analysis', methods=['GET'])
def skill_gap_analysis():
    return jsonify({"message": "Skill gap analysis stub"}), 200
