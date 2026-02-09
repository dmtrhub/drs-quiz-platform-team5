from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from app.schemas.user_schema import UserUpdateSchema, RoleChangeSchema, UserResponseSchema
from app.services.user_service import UserService
from app.utils.decorators import token_required, admin_required

users_bp = Blueprint('users', __name__)

user_update_schema = UserUpdateSchema()
role_change_schema = RoleChangeSchema()
user_response_schema = UserResponseSchema()


@users_bp.route('', methods=['GET'])
@admin_required
def list_users():
    try:
        users = UserService.list_all_users()
        return jsonify({
            "users": user_response_schema.dump(users, many=True)
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve users"}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    try:
        if g.user_id != user_id and g.user_role != 'ADMIN':
            return jsonify({"error": "Access denied"}), 403

        user = UserService.get_user(user_id)
        return jsonify({"user": user_response_schema.dump(user)}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to retrieve user"}), 500


@users_bp.route('/<int:user_id>/public', methods=['GET'])
def get_user_public(user_id):
    try:
        user = UserService.get_user(user_id)
        return jsonify({
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to retrieve user"}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    try:
        if g.user_id != user_id and g.user_role != 'ADMIN':
            return jsonify({"error": "Access denied"}), 403

        data = user_update_schema.load(request.get_json())

        user = UserService.update_user(user_id, data)

        return jsonify({
            "message": "User updated successfully",
            "user": user_response_schema.dump(user)
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        UserService.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Failed to delete user"}), 500


@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@admin_required
def change_role(user_id):
    try:
        data = role_change_schema.load(request.get_json())

        user = UserService.change_user_role(
            user_id,
            data['role'],
            g.user_id
        )

        return jsonify({
            "message": "Role changed successfully",
            "user": user_response_schema.dump(user)
        }), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to change role"}), 500
