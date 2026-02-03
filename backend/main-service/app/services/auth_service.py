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
        redis_client = current_app.redis_client
        failed_key = AuthService.FAILED_LOGIN_KEY.format(email)
        redis_client.delete(failed_key)

    @staticmethod
    def login_user(email, password, ip_address=None):
        """Login user and return JWT token"""
        if AuthService.is_user_blocked(email):
            redis_client = current_app.redis_client
            blocked_key = AuthService.BLOCKED_KEY.format(email)
            ttl = redis_client.ttl(blocked_key)

            if ttl > 0:
                if ttl < 60:
                    time_msg = f"{ttl} second(s)"
                else:
                    minutes = ttl // 60
                    seconds = ttl % 60
                    if seconds > 0:
                        time_msg = f"{minutes} minute(s) and {seconds} second(s)"
                    else:
                        time_msg = f"{minutes} minute(s)"
            else:
                time_msg = f"{AuthService.BLOCK_DURATION_MINUTES} minute(s)"

            raise ValueError(f"Account temporarily blocked due to multiple failed login attempts. Try again in {time_msg}.")

        user = User.query.filter_by(email=email).first()
        if not user:
            AuthService.track_failed_login(email, ip_address)
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            is_blocked = AuthService.track_failed_login(email, ip_address)

            if is_blocked:
                raise ValueError(f"Account blocked due to multiple failed login attempts. Try again in {AuthService.BLOCK_DURATION_MINUTES} minute(s).")
            else:
                raise ValueError("Invalid email or password")

        # Reset failed attempts
        AuthService.reset_failed_attempts(email)

        # Log successful attempt
        login_attempt = LoginAttempt(
            user_id=user.id,
            email=email,
            success=True,
            ip_address=ip_address
        )
        db.session.add(login_attempt)
        db.session.commit()

        token = generate_token(user.id, user.email, user.role.value)

        return user, token

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
