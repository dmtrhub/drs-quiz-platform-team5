from app import db
from app.models.user import User, RoleEnum
from app.models.login_attempt import LoginAttempt
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import generate_token
from flask import current_app
from datetime import datetime, timedelta

class AuthService:
    FAILED_LOGIN_KEY = "failed_login:{}"
    BLOCKED_KEY = "blocked:{}"
    MAX_FAILED_ATTEMPTS = 3
    BLOCK_DURATION_MINUTES = 1 
    @staticmethod
    def register_user(email, password, first_name, last_name, **kwargs):
        """Register new user"""
    existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError("Email already registered")

        password_hash = hash_password(password)

            # Create new user
            user = User(
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,          
                birth_date=kwargs.get('birth_date'),
                gender=kwargs.get('gender'),
                country=kwargs.get('country' ),
                street=kwargs.get('street', ''),
                street_number=str(kwargs.get('street_number')),
                role=RoleEnum.PLAYER  
            )

            db.session.add(user)
            db.session.commit()

            return user

    @staticmethod
    def login_user(email, password):
        """User login with rate limiting"""
        try:
            # Clean input
            email = email.strip().lower() if email else ''

            # Log login attempt (initially as failed)
            attempt = LoginAttempt(
                email=email,
                ip_address=request.remote_addr if request else None,
                user_agent=request.user_agent.string if request and request.user_agent else None,
                success=False
            )
            db.session.add(attempt)

            # Find user
            user = User.query.filter_by(email=email).first()

            if not user:
                db.session.commit()
                return None, {'email': 'Korisnik sa ovim email-om ne postoji'}, None

            # Check if account is active
            if not user.is_active:
                db.session.commit()
                return None, {'account': 'Korisnički nalog je deaktiviran'}, None

            # Check if account is blocked
            if user.is_login_blocked():
                blocked_time = user.get_blocked_time_remaining()
                db.session.commit()
                return None, {
                    'account': f'Prijava je blokirana. Pokušajte ponovo za {blocked_time} sekundi.'
                }, None

            # Verify password
            if not user.check_password(password):
                # Increment failed attempts
                user.failed_login_attempts += 1
                user.last_failed_login = datetime.now(pytz.UTC)

                # Block after 3 failed attempts (1 minute for testing)
                if user.failed_login_attempts >= 3:
                    user.login_blocked_until = datetime.now(pytz.UTC) + timedelta(minutes=1)

                db.session.commit()

                if user.failed_login_attempts >= 3:
                    return None, {
                        'account': 'Previše neuspješnih pokušaja. Pristup blokiran na 1 minut.'
                    }, None
                else:
                    attempts_left = 3 - user.failed_login_attempts
                    return None, {
                        'password': f'Pogrešna lozinka. Preostali pokušaji: {attempts_left}'
                    }, None

            # SUCCESSFUL LOGIN
            # Reset failed attempts
            user.reset_failed_logins()
            # Update login attempt to success
            attempt.success = True
            db.session.commit()

            # Create JWT tokens
            from flask_jwt_extended import create_access_token, create_refresh_token

            additional_claims = {
                'role': user.role,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )

            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )

            return user, None, {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Greška pri prijavi: {str(e)}")
            return None, {'error': str(e)}, None

    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            return User.query.get(int(user_id))
        except:
            return None

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change password"""
        user = User.query.get(int(user_id))

        if not user:
            return False, 'Korisnik nije pronađen'

        if not user.check_password(current_password):
            return False, 'Trenutna lozinka nije tačna'

        # Validate new password
        if len(new_password) < 8:
            return False, 'Nova lozinka mora imati najmanje 8 karaktera'
        if not re.search(r'[A-Z]', new_password):
            return False, 'Nova lozinka mora imati barem jedno veliko slovo'
        if not re.search(r'[a-z]', new_password):
            return False, 'Nova lozinka mora imati barem jedno malo slovo'
        if not re.search(r'\d', new_password):
            return False, 'Nova lozinka mora imati barem jedan broj'

        user.set_password(new_password)
        db.session.commit()

        return True, 'Lozinka uspješno promijenjena'
