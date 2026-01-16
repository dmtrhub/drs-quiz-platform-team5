from flask import request, jsonify, g
from datetime import datetime, timedelta
import time
import redis
import functools
from src import db
from src.models.user import User
import pytz


class RateLimiter:
    """Middleware za rate limiting"""

    @staticmethod
    def login_rate_limit(f):
        """Decorator za rate limiting prijave"""

        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            email = request.get_json().get('email') if request.is_json else None

            if not email:
                return jsonify({'error': 'Email je obavezan'}), 400

            # Pronađi korisnika
            user = User.query.filter_by(email=email.strip().lower()).first()

            if user:
                # Proveri da li je blokiran
                if user.is_login_blocked():
                    blocked_time = user.get_blocked_time_remaining()
                    return jsonify({
                        'error': 'Previše neuspješnih pokušaja',
                        'message': f'Prijava je blokirana. Pokušajte za {blocked_time} sekundi.',
                        'blocked_until': user.login_blocked_until.isoformat() if user.login_blocked_until else None,
                        'attempts_left': 0
                    }), 429

            return f(*args, **kwargs)

        return decorated_function

    @staticmethod
    def api_rate_limit(requests_per_minute=100):
        """Decorator za general API rate limiting"""

        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                # U produkciji bi ovde koristili Redis
                # Za sada vraćamo originalnu funkciju
                return f(*args, **kwargs)

            return decorated_function

        return decorator


def track_login_attempt(email, success):
    """Prati pokušaje prijave"""
    from src.models.user import LoginAttempt

    try:
        attempt = LoginAttempt(
            email=email,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if request.user_agent else None,
            success=success
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Loguj grešku ali ne prekida izvršenje
        pass