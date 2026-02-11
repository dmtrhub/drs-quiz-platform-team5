from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import redis
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY')

    app.config['MAIL_SERVER'] = app.config.get('MAIL_SERVER', None)
    app.config['MAIL_PORT'] = app.config.get('MAIL_PORT', 587)
    app.config['MAIL_USE_TLS'] = app.config.get('MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = app.config.get('MAIL_USERNAME', None)
    app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASSWORD', None)
    app.config['MAIL_DEFAULT_SENDER'] = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@quizplatform.com')

    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    from app.services.email_service import EmailService
    EmailService.init_mail(app)

    from app.websocket.events import register_socketio_events
    register_socketio_events(socketio)

    app.redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379/0'))

    from app.models.user import User
    from app.models.login_attempt import LoginAttempt
    from app.models.audit_log import AuditLog

    with app.app_context():
        db.create_all()

    @app.route("/test-db1")
    def test_db1():
        try:
            result = db.session.execute(db.text("SELECT version();")).fetchone()
            return {
                "status": "ok",
                "postgres_version": str(result[0])[:100]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    @app.route("/test-redis")
    def test_redis():
        try:
            app.redis_client.set('test_key', 'test_value', ex=60)
            value = app.redis_client.get('test_key')
            app.redis_client.delete('test_key')
            return {
                "status": "ok",
                "test_result": value.decode('utf-8') if value else None
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1;"))
            app.redis_client.ping()
            return {"status": "ok", "service": "main-service"}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    @app.route("/")
    def index(): return {"status": "ok", "service": "main-service"}	

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.notifications import notifications_bp
    from app.routes.quiz_proxy import quiz_proxy_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(notifications_bp, url_prefix='/api/notify')
    app.register_blueprint(quiz_proxy_bp)  

    return app

