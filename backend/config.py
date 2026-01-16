import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'postgresql://postgres:postgres@localhost:5432/quiz_db1')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Postgres-specific options (ONLY for PostgreSQL)
    if SQLALCHEMY_DATABASE_URI and 'postgresql' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'pool_size': 10,
            'max_overflow': 20,
        }
    else:
        # For SQLite and other databases
        SQLALCHEMY_ENGINE_OPTIONS = {}

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@quizplatform.com')
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'True').lower() == 'true'  # TRUE za test

    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Security
    PASSWORD_MIN_LENGTH = 8
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    LOGIN_ATTEMPT_LIMIT = 3
    LOGIN_BLOCK_TIME_MINUTES = 1  # 1 min za test


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SUPPRESS_SEND = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MAIL_SUPPRESS_SEND = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # Disable rate limiting for tests
    RATE_LIMIT_ENABLED = False
    LOGIN_ATTEMPT_LIMIT = 100


class ProductionConfig(Config):
    DEBUG = False
    MAIL_SUPPRESS_SEND = False
    SESSION_COOKIE_SECURE = True
    LOGIN_BLOCK_TIME_MINUTES = 15


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}