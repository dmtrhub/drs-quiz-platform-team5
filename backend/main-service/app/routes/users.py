from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import pytz

from ..services.user_service import UserService
from ..services.auth_service import AuthService
from ..models.user import User, LoginAttempt
from .. import db

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Samo administrator može pristupiti listi korisnika'}), 403

        # Pagination and filtering
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        role = request.args.get('role')
        search = request.args.get('search')
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'

        if limit > 100:
            limit = 100

        result = UserService.get_all_users(
            limit=limit,
            offset=offset,
            role=role,
            search=search,
            active_only=not include_inactive
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri dobijanju korisnika: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Nemate permisiju za ovu akciju'}), 403

        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({'error': 'Uloga je obavezna'}), 400

        new_role = data['role']

        success, message = UserService.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin_id=current_user_id
        )

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({'message': message}), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri promjeni uloge: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user account (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Nemate permisiju za ovu akciju'}), 403

        success, message = UserService.delete_user(
            user_id=user_id,
            admin_id=current_user_id
        )

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({'message': message}), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri brisanju korisnika: {str(e)}'}), 500


@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get user statistics (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Samo administrator može pristupiti statistici'}), 403

        stats = UserService.get_user_stats()
        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri dobijanju statistike: {str(e)}'}), 500


@users_bp.route('/login-attempts', methods=['GET'])
@jwt_required()
def get_login_attempts():
    """Get login attempts (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Samo administrator može pristupiti login pokušajima'}), 403

        email = request.args.get('email')
        limit = request.args.get('limit', 100, type=int)

        query = LoginAttempt.query

        if email:
            query = query.filter_by(email=email)

        attempts = query.order_by(
            LoginAttempt.attempted_at.desc()
        ).limit(limit).all()

        return jsonify({
            'attempts': [attempt.to_dict() for attempt in attempts],
            'total': len(attempts)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri dobijanju login pokušaja: {str(e)}'}), 500


@users_bp.route('/blocked', methods=['GET'])
@jwt_required()
def get_blocked_users():
    """Get blocked users (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Samo administrator može pristupiti listi blokiranih'}), 403

        all_users = User.query.filter_by(is_active=True).all()
        blocked_users = [
            user for user in all_users
            if user.is_login_blocked()
        ]

        return jsonify({
            'blocked_users': [user.to_dict() for user in blocked_users],
            'total': len(blocked_users)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri dobijanju blokiranih korisnika: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/unblock', methods=['POST'])
@jwt_required()
def unblock_user(user_id):
    """Unblock user (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Samo administrator može deblokirati korisnike'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Korisnik nije pronađen'}), 404

        success, message = UserService.unblock_user(user_id, current_user_id)

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({
            'message': 'Korisnik uspešno deblokiran',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri deblokiranju korisnika: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@jwt_required()
def activate_user(user_id):
    """Activate user account (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = AuthService.get_user_by_id(current_user_id)

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Samo administrator može aktivirati naloge'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Korisnik nije pronađen'}), 404

        success, message = UserService.activate_user(user_id, current_user_id)

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({'message': 'Korisnički nalog uspešno aktiviran'}), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri aktiviranju korisnika: {str(e)}'}), 500