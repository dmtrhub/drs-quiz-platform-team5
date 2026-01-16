from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import func
import pytz

from ..models.user import User
from .. import db
from ..utils.email_service import EmailService


class UserService:
    @staticmethod
    def get_all_users(limit=50, offset=0, role=None, search=None, active_only=True):
        """Get all users with pagination and filtering"""
        query = User.query

        if active_only:
            query = query.filter_by(is_active=True)

        if role:
            query = query.filter_by(role=role)

        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )

        total = query.count()
        users = query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()

        return {
            'users': [user.to_dict() for user in users],
            'total': total,
            'limit': limit,
            'offset': offset
        }

    @staticmethod
    def update_user_profile(user_id, update_data):
        """Update user profile"""
        user = User.query.get(int(user_id))
        if not user:
            return None, {'error': 'Korisnik nije pronađen'}

        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'date_of_birth', 'gender',
                          'country', 'street', 'street_number']

        for field in allowed_fields:
            if field in update_data:
                if field == 'date_of_birth':
                    try:
                        setattr(user, field, datetime.strptime(update_data[field], '%Y-%m-%d').date())
                    except ValueError:
                        return None, {field: 'Nevažeći format datuma. Koristite YYYY-MM-DD'}
                else:
                    setattr(user, field,
                            update_data[field].strip() if isinstance(update_data[field], str) else update_data[field])

        try:
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri ažuriranju profila: {str(e)}")
            return None, {'database': str(e)}

    @staticmethod
    def update_user_role(user_id, new_role, admin_id):
        """Update user role (admin only)"""
        valid_roles = ['player', 'moderator', 'admin']

        if new_role not in valid_roles:
            return False, 'Nevažeća uloga'

        user = User.query.get(int(user_id))
        admin = User.query.get(int(admin_id))

        if not user or not admin:
            return False, 'Korisnik ili administrator nisu pronađeni'

        if admin.role != 'admin':
            return False, 'Samo administrator može mijenjati uloge'

        old_role = user.role

        # If role is the same, return success
        if old_role == new_role:
            return True, 'Uloga je već postavljena'

        user.role = new_role

        try:
            db.session.commit()

            # Send email about role change
            try:
                EmailService.send_role_change_email(user, old_role, new_role)
            except Exception as e:
                current_app.logger.error(f"Greška pri slanju email-a za promjenu uloge: {str(e)}")

            return True, f'Uloga uspješno promijenjena iz {old_role} u {new_role}'

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri promjeni uloge: {str(e)}")
            return False, 'Greška pri čuvanju podataka'

    @staticmethod
    def delete_user(user_id, admin_id):
        """Delete user account (admin only) - soft delete"""
        user = User.query.get(int(user_id))
        admin = User.query.get(int(admin_id))

        if not user or not admin:
            return False, 'Korisnik ili administrator nisu pronađeni'

        if admin.role != 'admin':
            return False, 'Samo administrator može brisati naloge'

        if user.id == admin.id:
            return False, 'Ne možete obrisati svoj nalog'

        # Soft delete - deactivate user
        user.is_active = False
        # Modify email to prevent re-registration
        user.email = f"{user.email}_deleted_{datetime.now().timestamp()}"

        try:
            db.session.commit()
            return True, 'Korisnički nalog uspješno deaktiviran'

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri brisanju korisnika: {str(e)}")
            return False, 'Greška pri brisanju podataka'

    @staticmethod
    def activate_user(user_id, admin_id):
        """Activate user account (admin only)"""
        user = User.query.get(int(user_id))
        admin = User.query.get(int(admin_id))

        if not user or not admin:
            return False, 'Korisnik ili administrator nisu pronađeni'

        if admin.role != 'admin':
            return False, 'Samo administrator može aktivirati naloge'

        user.is_active = True

        try:
            db.session.commit()
            return True, 'Korisnički nalog uspješno aktiviran'
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri aktiviranju korisnika: {str(e)}")
            return False, 'Greška pri aktiviranju naloga'

    @staticmethod
    def get_user_stats():
        """Get user statistics"""
        from sqlalchemy import func
        from datetime import datetime, timedelta
        import pytz

        # Users by role
        role_stats = db.session.query(
            User.role,
            func.count(User.id)
        ).filter(User.is_active == True).group_by(User.role).all()

        # Total users
        total_users = User.query.filter_by(is_active=True).count()

        # New users in last 30 days
        thirty_days_ago = datetime.now(pytz.UTC) - timedelta(days=30)
        new_users = User.query.filter(
            User.created_at >= thirty_days_ago,
            User.is_active == True
        ).count()

        # Blocked users
        all_active_users = User.query.filter_by(is_active=True).all()
        blocked_users = 0
        for user in all_active_users:
            if user.is_login_blocked():
                blocked_users += 1

        return {
            'total_users': total_users,
            'new_users_last_30_days': new_users,
            'blocked_users': blocked_users,
            'roles': {role: count for role, count in role_stats}
        }

    @staticmethod
    def get_blocked_users():
        """Get list of blocked users"""
        all_users = User.query.filter_by(is_active=True).all()
        blocked_users = [
            user for user in all_users
            if user.is_login_blocked()
        ]

        return blocked_users

    @staticmethod
    def unblock_user(user_id, admin_id):
        """Unblock user (admin only)"""
        user = User.query.get(int(user_id))
        admin = User.query.get(int(admin_id))

        if not user or not admin:
            return False, 'Korisnik ili administrator nisu pronađeni'

        if admin.role != 'admin':
            return False, 'Samo administrator može deblokirati korisnike'

        user.reset_failed_logins()
        db.session.commit()

        return True, 'Korisnik uspešno deblokiran'