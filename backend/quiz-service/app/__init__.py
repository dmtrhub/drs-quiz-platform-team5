from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-secret')

    CORS(app)
    jwt.init_app(app)

    app.mongo_client = MongoClient(app.config['MONGO_URI'])
    app.mongo_db = app.mongo_client[app.config.get('MONGO_DB', 'quiz_db')]

    from app.models.quiz import QuizModel
    from app.models.result import ResultModel

    app.quiz_model = QuizModel(app.mongo_db)
    app.result_model = ResultModel(app.mongo_db)

    app.mongo_db.quizzes.create_index('status')
    app.mongo_db.quizzes.create_index('author_id')
    app.mongo_db.results.create_index('quiz_id')
    app.mongo_db.results.create_index('user_id')
    app.mongo_db.results.create_index([('quiz_id', 1), ('score', -1)])

    @app.route("/test-db2")
    def test_db2():
        try:
            app.mongo_db.command('ping')

            test_collection = app.mongo_db.test
            test_collection.insert_one({"test": "hello"})
            count = test_collection.count_documents({})
            test_collection.delete_many({})

            return {
                "status": "ok",
                "collections": list(app.mongo_client.list_database_names()),
                "test_count": count
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    @app.route("/health")
    def health():
        try:
            app.mongo_db.command('ping')
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
