from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.notifications import notifications_bp
    from app.routes.quiz_proxy import quiz_proxy_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(notifications_bp, url_prefix='/api/notify')
    app.register_blueprint(quiz_proxy_bp)  

    return app
