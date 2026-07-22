from flask import jsonify
from datetime import datetime, timezone

def format_response(success: bool, message: str, data: dict = None, status_code: int = 200):
    response = {
        "success": success,
        "message": message,
        "data": data if data is not None else {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(response), status_code

def success_response(message: str, data: dict = None, status_code: int = 200):
    return format_response(True, message, data, status_code)

def error_response(message: str, status_code: int = 400):
    return format_response(False, message, None, status_code)
