from flask import Blueprint, jsonify, request

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    return jsonify({"message": "Register endpoint stub"}), 201

@bp.route('/login', methods=['POST'])
def login():
    return jsonify({"message": "Login endpoint stub"}), 200
