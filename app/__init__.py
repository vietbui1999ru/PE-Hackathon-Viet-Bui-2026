from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes

import logging
import json
import time

# logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record),
            "logger": record.name,
        })

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

def create_app():
    load_dotenv()
    from prometheus_flask_exporter import PrometheusMetrics
    metrics = PrometheusMetrics(app)

    app = Flask(__name__)



    register_routes(app)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    init_db(app)

    with app.app_context():
        from app.database import db  # noqa: F401
        from app.models import User, Url, Event  # noqa: F401 - registers models with Peewee

        db.connect(reuse_if_open=True)
        db.create_tables([User, Url, Event], safe=True)
        db.close()

    @app.route("/metrics")
    def metrics():
        return jsonify({
            "cpu_percent": psutil.cpu_percent(),
            "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
            "memory_percent": psutil.virtual_memory().percent,
            "uptime_seconds": time.time() - app.start_time
        })

    app.start_time = time.time()

    return app
