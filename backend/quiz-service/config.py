import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    INTERNAL_SERVICE_TOKEN = os.environ.get("INTERNAL_SERVICE_TOKEN")
    CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin@localhost:27017/quiz_db?authSource=admin")
    MONGO_DB = os.environ.get("MONGO_DB", "quiz_db")
    MAIN_SERVICE_URL = os.environ.get("MAIN_SERVICE_URL", "http://localhost:5000")
    RESULT_PROCESSING_DELAY_SECONDS = int(os.environ.get("RESULT_PROCESSING_DELAY_SECONDS", 0))