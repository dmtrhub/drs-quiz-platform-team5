from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            jwt_data = get_jwt()

            g.user_id = int(user_id) if isinstance(user_id, str) else user_id
            g.user_role = jwt_data.get('role')
            g.user_email = jwt_data.get('email')

            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401

    return wrapper


def admin_required(func):
    @wraps(func)
    @token_required
    def wrapper(*args, **kwargs):
        if g.user_role != 'ADMIN':
            return jsonify({"error": "Admin access required"}), 403
        return func(*args, **kwargs)

    return wrapper


def moderator_required(func):
    @wraps(func)
    @token_required
    def wrapper(*args, **kwargs):
        if g.user_role not in ['MODERATOR', 'ADMIN']:
            return jsonify({"error": "Moderator or Admin access required"}), 403
        return func(*args, **kwargs)

    return wrapper
