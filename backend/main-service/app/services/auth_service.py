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
    def is_user_blocked(email):
        """Check if user is blocked due to failed login attempts"""
        redis_client = current_app.redis_client
        blocked_key = AuthService.BLOCKED_KEY.format(email)
        return redis_client.exists(blocked_key)

     @staticmethod
    def track_failed_login(email, ip_address=None):
        """Track failed login attempt"""
        redis_client = current_app.redis_client
        failed_key = AuthService.FAILED_LOGIN_KEY.format(email)

        failed_count = redis_client.incr(failed_key)
        redis_client.expire(failed_key, 300) 

        user = User.query.filter_by(email=email).first()
        login_attempt = LoginAttempt(
            user_id=user.id if user else None,
            email=email,
            success=False,
            ip_address=ip_address
        )
        db.session.add(login_attempt)
        db.session.commit()

        # Block user if max attempts reached
        if failed_count >= AuthService.MAX_FAILED_ATTEMPTS:
            AuthService.block_user(email)
            return True  

        return False

    @staticmethod
    def block_user(email):
        """Block user for a duration"""
        redis_client = current_app.redis_client
        blocked_key = AuthService.BLOCKED_KEY.format(email)
        redis_client.setex(
            blocked_key,
            AuthService.BLOCK_DURATION_MINUTES * 60,
            "blocked"
        )

    @staticmethod
    def reset_failed_attempts(email):
        """Reset failed login attempts after successful login"""
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


