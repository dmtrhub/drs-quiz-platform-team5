import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:admin@localhost:27017/quiz_db?authSource=admin")
    MONGO_DB = os.environ.get("MONGO_DB", "quiz_db")
    MAIN_SERVICE_URL = os.environ.get("MAIN_SERVICE_URL", "http://localhost:5000")