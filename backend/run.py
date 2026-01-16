#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))

    print(f"Starting Quiz Platform Backend on {host}:{port}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")

    app.run(host=host, port=port, debug=True)