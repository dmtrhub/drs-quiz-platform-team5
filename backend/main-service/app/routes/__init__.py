from .auth import auth_bp
from .users import users_bp
from .notifications import notifications_bp
from .quiz_proxy import quiz_proxy_bp

__all__ = ['auth_bp', 'users_bp', 'notifications_bp', 'quiz_proxy_bp']