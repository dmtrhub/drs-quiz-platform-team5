from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import redis
from config import Config

jwt = JWTManager()


def _parse_allowed_origins(raw_origins):
    if not raw_origins:
        return "*"

    raw = str(raw_origins).strip()
    if raw == "*":
        return "*"

    parsed = [origin.strip() for origin in raw.split(',') if origin.strip()]
    return parsed or "*"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError("SECRET_KEY is required")
    if not app.config.get('INTERNAL_SERVICE_TOKEN'):
        raise RuntimeError("INTERNAL_SERVICE_TOKEN is required")

    allowed_origins = _parse_allowed_origins(app.config.get('CORS_ALLOWED_ORIGINS'))

    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY')

    CORS(app, origins=allowed_origins)
    jwt.init_app(app)

    app.mongo_client = MongoClient(app.config['MONGO_URI'])
    app.mongo_db = app.mongo_client[app.config.get('MONGO_DB', 'quiz_db')]
    app.redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379/0'))

    from app.models.quiz import QuizModel
    from app.models.result import ResultModel

    app.quiz_model = QuizModel(app.mongo_db)
    app.result_model = ResultModel(app.mongo_db)

    app.mongo_db.quizzes.create_index('status')
    app.mongo_db.quizzes.create_index('author_id')
    app.mongo_db.results.create_index('quiz_id')
    app.mongo_db.results.create_index('user_id')
    app.mongo_db.results.create_index([('quiz_id', 1), ('score', -1)])

    @app.route("/health")
    def health():
        try:
            app.mongo_db.command('ping')
            app.redis_client.ping()
            return {"status": "ok", "service": "quiz-service"}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    from app.routes.quiz import quiz_bp
    from app.routes.results import results_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(quiz_bp, url_prefix='/quizzes')
    app.register_blueprint(results_bp, url_prefix='/results')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app
