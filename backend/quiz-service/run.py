import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()


def is_debug_enabled() -> bool:
    return os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes", "on")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=is_debug_enabled())

