from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes


def create_app():
    load_dotenv()

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

    return app
