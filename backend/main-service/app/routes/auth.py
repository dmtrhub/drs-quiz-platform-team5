from datetime import datetime, timezone

import pytz
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.utils import secure_filename
import os

from ..services.auth_service import AuthService
from ..models.user import User
from .. import db

auth_bp = Blueprint('auth', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user - FIXED VERSION"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Nema podataka'}), 400

        user, errors = AuthService.register_user(data)

        if errors:
            return jsonify({'errors': errors}), 400

        # Check if user object is valid
        if not user or not hasattr(user, 'id'):
            return jsonify({'error': 'Greška pri kreiranju korisnika'}), 500

        # Create JWT tokens
        from flask_jwt_extended import create_access_token, create_refresh_token

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Registracija uspešna',
            'user': user.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"Greška u register endpointu: {str(e)}")
        return jsonify({'error': f'Greška pri registraciji: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Nema podataka'}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email i lozinka su obavezni'}), 400

        user, errors, tokens = AuthService.login_user(email, password)

        if errors:
            return jsonify({'errors': errors}), 401

        return jsonify({
            'message': 'Prijava uspešna',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri prijavi: {str(e)}'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)

        if not user or not user.is_active:
            return jsonify({'error': 'Korisnik nije pronađen ili je deaktiviran'}), 401

        new_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': new_token}), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri osvežavanju tokena: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout"""
    return jsonify({'message': 'Odjava uspešna'}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)

        if not user:
            return jsonify({'error': 'Korisnik nije pronađen'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri dobijanju profila: {str(e)}'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        from ..services.user_service import UserService

        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Nema podataka'}), 400

        user, errors = UserService.update_user_profile(user_id, data)

        if errors:
            return jsonify({'errors': errors}), 400

        return jsonify({
            'message': 'Profil uspešno ažuriran',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri ažuriranju profila: {str(e)}'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Nema podataka'}), 400

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({'error': 'Trenutna i nova lozinka su obavezne'}), 400

        success, message = AuthService.change_password(
            user_id, current_password, new_password
        )

        if not success:
            return jsonify({'error': message}), 400

        return jsonify({'message': message}), 200

    except Exception as e:
        return jsonify({'error': f'Greška pri promeni lozinke: {str(e)}'}), 500


@auth_bp.route('/profile/image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    """Upload profile image"""
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)

        if not user:
            return jsonify({'error': 'Korisnik nije pronađen'}), 404

        if 'image' not in request.files:
            return jsonify({'error': 'Nema slike u zahtevu'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'Nije odabrana datoteka'}), 400

        if file and allowed_file(file.filename):
            # Create upload directory
            upload_folder = 'uploads/profile_images'
            os.makedirs(upload_folder, exist_ok=True)

            # Generate unique filename
            filename = secure_filename(f"{user.id}_{file.filename}")
            filepath = os.path.join(upload_folder, filename)

            # Save file
            file.save(filepath)

            # Update user
            user.profile_image = filename
            db.session.commit()

            return jsonify({
                'message': 'Slika uspešno uploadovana',
                'image_url': f'/api/auth/profile/image/{filename}'
            }), 200

        return jsonify({'error': 'Tip datoteke nije dozvoljen. Dozvoljeni: png, jpg, jpeg, gif'}), 400

    except Exception as e:
        return jsonify({'error': f'Greška pri uploadu slike: {str(e)}'}), 500


@auth_bp.route('/profile/image/<filename>', methods=['GET'])
def get_profile_image(filename):
    """Serve profile image"""
    try:
        upload_folder = 'uploads/profile_images'
        filepath = os.path.join(upload_folder, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'Slika nije pronađena'}), 404

        return send_from_directory(upload_folder, filename)

    except Exception as e:
        return jsonify({'error': f'Greška pri dobijanju slike: {str(e)}'}), 500


@auth_bp.route('/test/rate-limit', methods=['POST'])
def test_rate_limit():
    """Test endpoint for rate limiting demonstration"""
    try:
        data = request.get_json()
        email = data.get('email', 'test@example.com')

        user = User.query.filter_by(email=email).first()

        if user:
            # Simulate failed login
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.now(pytz.UTC)

            # Block after 3 attempts
            if user.failed_login_attempts >= 3:
                from datetime import timedelta
                user.login_blocked_until = datetime.now(pytz.UTC) + timedelta(minutes=1)

            db.session.commit()

            if user.failed_login_attempts >= 3:
                return jsonify({
                    'error': 'Račun je blokiran',
                    'blocked_until': user.login_blocked_until.isoformat() if user.login_blocked_until else None,
                    'attempts': user.failed_login_attempts,
                    'blocked_time_remaining': user.get_blocked_time_remaining()
                }), 429
            else:
                attempts_left = 3 - user.failed_login_attempts
                return jsonify({
                    'message': f'Neuspješna prijava. Preostali pokušaji: {attempts_left}',
                    'attempts': user.failed_login_attempts
                }), 401

        return jsonify({'error': 'Korisnik nije pronađen'}), 404

    except Exception as e:
        return jsonify({'error': f'Greška pri testu rate limita: {str(e)}'}), 500