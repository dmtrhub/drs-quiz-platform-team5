from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.auth_schema import RegisterSchema, LoginSchema, AuthResponseSchema
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

auth_bp = Blueprint('auth', __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
auth_response_schema = AuthResponseSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user - FIXED VERSION"""
    try:
        data = register_schema.load(request.get_json())

        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=data.get('birth_date'),
            gender=data.get('gender'),
            country=data.get('country'),
            street=data.get('street'),
            street_number=data.get('street_number'),
            profile_image=data.get('profile_image')
        )

        EmailService.send_registration_email(user)

        response_data = auth_response_schema.dump({
            "message": "User registered successfully",
            "user": user
        })
        return jsonify(response_data), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = login_schema.load(request.get_json())

        ip_address = request.remote_addr

        user, token = AuthService.login_user(
            email=data['email'],
            password=data['password'],
            ip_address=ip_address
        )

        response_data = auth_response_schema.dump({
            "message": "Login successful",
            "access_token": token,
            "user": user
        })
        return jsonify(response_data), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Login failed"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    return jsonify({"message": "Logout successful"}), 200