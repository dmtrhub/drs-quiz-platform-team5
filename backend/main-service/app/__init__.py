from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
