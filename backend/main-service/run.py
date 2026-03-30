from dotenv import load_dotenv
import os

load_dotenv()

from app import create_app, socketio
app = create_app()


def is_debug_enabled() -> bool:
    return os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes", "on")


def is_unsafe_werkzeug_allowed() -> bool:
    return os.environ.get("ALLOW_UNSAFE_WERKZEUG", "false").lower() in ("1", "true", "yes", "on")

if __name__ == "__main__":
    debug_mode = is_debug_enabled()
    allow_unsafe = is_unsafe_werkzeug_allowed()
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=debug_mode,
        allow_unsafe_werkzeug=allow_unsafe,
    )


