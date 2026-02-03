from app import db
from app.models.user import User, RoleEnum
from app.models.audit_log import AuditLog
from app.services.email_service import EmailService
from app.utils.password_utils import hash_password, verify_password
from datetime import datetime, date


class UserService:
    @staticmethod
    def get_all_users(limit=50, offset=0, role=None, search=None, active_only=True):
        """Get all user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        return user

    @staticmethod 
    def list_all_users():
        """List all users"""
        users = User.query.all()
        return users

    @staticmethod
    def update_user(user_id, data):
        """Update user profile"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

            if 'new_password' in update_data and update_data['new_password']:
                if 'current_password' not in update_data or not update_data['current_password']:
                    raise ValueError("Current password is required to change password")

            if not verify_password(data['current_password'], user.password_hash):
                raise ValueError("Current password is incorrect")

            user.password_hash = hash_password(data['new_password'])
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'birth_date' in data:
            if isistance(data['birth_date'], str):
                try: 
                    user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                except ValueError:
                      raise ValueError("Invalid birth date format. Use YYYY-MM-DD")
            else:
                user.birth_date = data['birth_date']

        if 'gender' in data:
            user.gender = data['gender']
        if 'country' in data:
            user.country = data['country']
        if 'street' in data:
            user.street = data['street']
        if 'street_number' in data:
            user.street_number = data['street_number']
        if 'profile_image' in data:
            user.profile_image = data['profile_image']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return user    

    @staticmethod
    def delete_user(user_id, admin_id):
        """Delete user account (admin only) - soft delete"""
        user = User.query.get(int(user_id))
        if not user:
            raise ValueError("User not found")

        db.session.delete(user)
        db.session.commit()

        return True

    @staticmethod
    def change_user_role(user_id, new_role, admin_id):
        """Change user role (admin only)"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if new_role not in ['PLAYER', 'MODERATOR', 'ADMIN']:
            raise ValueError("Invalid role")

        old_role = user.role.value
        user.role = RoleEnum(new_role)
        user.updated_at = datetime.utcnow()

        audit_log = AuditLog(user_id=admin_id,
                             action=f'Changed role of user {user_id}',
                             details=f'Changed from {old_role} to {new_role}')

        db.session.add(audit_log)
        db.session.commit()

        EmailService.send_role_change_email(user, old_role, new_role) 
    
        return user



