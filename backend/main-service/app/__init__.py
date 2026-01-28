from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
cors = CORS()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    from config import config
    app.config.from_object(config[config_name])

    # **FIX: Remove engine options for SQLite**
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # JWT configuration
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, str):
            return user
        # Ako je User objekat, vrati ID kao string
        return str(user.id) if user else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from .models.user import User
        identity = jwt_data["sub"]
        # identity je string ID
        return User.query.filter_by(id=int(identity)).one_or_none()

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from .dto.base_dto import ErrorResponseDTO
        error = ErrorResponseDTO(
            error='Token Expired',
            message='Token je istekao. Prijavite se ponovo.'
        )
        return jsonify(error.dict()), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from .dto.base_dto import ErrorResponseDTO
        error = ErrorResponseDTO(
            error='Invalid Token',
            message=f'Nevažeći token: {str(error)}'
        )
        return jsonify(error.dict()), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        from .dto.base_dto import ErrorResponseDTO
        error = ErrorResponseDTO(
            error='Unauthorized',
            message='Zahtev zahteva autentifikaciju. Token nedostaje u zahtevu.'
        )
        return jsonify(error.dict()), 401

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from .dto.base_dto import SuccessResponseDTO
        response = SuccessResponseDTO(
            message='Service is healthy',
            data={
                'status': 'healthy',
                'service': 'Quiz Platform Backend',
                'environment': app.config['FLASK_ENV']
            }
        )
        return jsonify(response.dict()), 200

    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created successfully")

    return app