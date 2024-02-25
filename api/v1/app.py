#!/usr/bin/python3
"""app.py to connect to API"""
# api/v1/app.py
from flask import Flask
from models import storage
from api.v1.views import app_views
from flask_cors import CORS
import os

app = Flask(__name__)

# Allow CORS for all routes on the API (/*) for 0.0.0.0
CORS(app, resources={r"/api/*": {"origins": "0.0.0.0"}})

app.register_blueprint(app_views)

@app.teardown_appcontext
def close_storage(exception):
    """Remove the current SQLAlchemy Session"""
    storage.close()

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("HBNB_API_PORT", 5000))
    app.run(host=host, port=port, threaded=True)
