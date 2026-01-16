from datetime import datetime, date, timedelta
from .. import db
import bcrypt
import pytz


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # 'male', 'female', 'other'
    country = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    street_number = db.Column(db.String(20), nullable=False)
    profile_image = db.Column(db.String(500))
    role = db.Column(db.String(20), default='player', nullable=False)  # 'player', 'moderator', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(pytz.UTC),
        onupdate=lambda: datetime.now(pytz.UTC)
    )

    # Rate limiting fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    login_blocked_until = db.Column(db.DateTime)
    last_failed_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

    def set_password(self, password):
        """Hash and store password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Verify password - FIXED"""
        if not self.password_hash:
            return False

        try:
            # Convert password_hash to bytes if it's a string
            if isinstance(self.password_hash, str):
                hash_bytes = self.password_hash.encode('utf-8')
            else:
                hash_bytes = self.password_hash

            # Verify password
            return bcrypt.checkpw(password.encode('utf-8'), hash_bytes)
        except:
            return False

    def increment_failed_login(self):
        """Increment failed login attempts and block if needed"""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.now(pytz.UTC)

        # Block after 3 failed attempts
        if self.failed_login_attempts >= 3:
            from .. import app
            block_minutes = app.config.get('LOGIN_BLOCK_TIME_MINUTES', 1)
            self.login_blocked_until = datetime.now(pytz.UTC) + timedelta(minutes=block_minutes)

        return self.failed_login_attempts

    def reset_failed_logins(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.login_blocked_until = None
        self.last_failed_login = None

    def is_login_blocked(self):
        """Check if user is blocked from logging in"""
        if not self.login_blocked_until:
            return False

        # Ensure timezone awareness
        blocked_until = self.login_blocked_until
        if blocked_until.tzinfo is None:
            blocked_until = pytz.UTC.localize(blocked_until)

        current_time = datetime.now(pytz.UTC)
        return current_time < blocked_until

    def get_blocked_time_remaining(self):
        """Get remaining block time in seconds"""
        if not self.is_login_blocked():
            return 0

        blocked_until = self.login_blocked_until
        if blocked_until.tzinfo is None:
            blocked_until = pytz.UTC.localize(blocked_until)

        current_time = datetime.now(pytz.UTC)
        remaining = blocked_until - current_time
        return max(0, int(remaining.total_seconds()))

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'country': self.country,
            'street': self.street,
            'street_number': self.street_number,
            'profile_image': self.profile_image,
            'profile_image_url': f'/api/auth/profile/image/{self.profile_image}' if self.profile_image else None,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'failed_login_attempts': self.failed_login_attempts,
            'is_login_blocked': self.is_login_blocked(),
            'blocked_time_remaining': self.get_blocked_time_remaining()
        }


class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    success = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None
        }
