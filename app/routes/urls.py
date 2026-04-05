from datetime import datetime, timezone
import uuid
from flask.globals import request
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.urls import Url
from app.models.events import Event

from peewee import IntegrityError

import json

urls_bp = Blueprint("urls", __name__)


@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    # add pagination later
    query = Url.select()
    if request.args.get("is_active"):
        is_active = request.args.get("is_active").lower() == "true"
        query = query.where(Url.is_active == is_active)
    if request.args.get("user_id"):
        user_id = request.args.get("user_id")
        query = query.where(Url.user_id == int(user_id))
    # model_to_dict return controlled fields for each u in urls
    return jsonify({"data" : [model_to_dict(u) for u in query]})

@urls_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json()

    try:
        data["user_id"] = int(data["user_id"])
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    if not data or "original_url" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    if not data["original_url"].startswith("http://") and not data["original_url"].startswith("https://"):
        return jsonify({"error": "Invalid url"}), 400
    if not data or "original_url" not in data or "user_id" not in data:
            return jsonify({"error": "original url is required, user id is required"}), 400
        # check short code exist in database, return 400 alrady exist
    if "short_code" in data:
        if Url.get_or_none(Url.short_code == data["short_code"] and Url.is_active == True):
            return jsonify({"error": "short code already exist"}), 400

    try:
        url = Url.create(original_url=data["original_url"], 
                     title=data["title"] if "title" in data else None,
                     user_id=data["user_id"] if "user_id" in data else None,
                     short_code=uuid.uuid4().hex[:8] if "short_code" not in data else data["short_code"])
    except IntegrityError:
        return jsonify({"error": "Url already exists"}), 409
    return jsonify(model_to_dict(url)), 201

@urls_bp.route("/urls/<int:url_id>", methods=["GET"])
def get_url(url_id):
    data = Url.get_or_none(Url.id == url_id)
    if not data:
        return jsonify({"error": "Url not found"}), 404

    return jsonify(model_to_dict(data)), 200

@urls_bp.route("/urls/<int:url_id>", methods=["PUT"])
def update_url(url_id):
    data = Url.get_or_none(Url.id == url_id)
    if not data:
        return jsonify({"error": "Url not found"}), 404

    update_data = request.get_json()
    if "original_url" in update_data:
        data.original_url = update_data["original_url"]
    if "title" in update_data:
        data.title = update_data["title"]
    if "is_active" in update_data:
        data.is_active = update_data["is_active"]

    data.updated_at = datetime.now(timezone.utc)
    data.save()
    return jsonify(model_to_dict(data)), 200

@urls_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    data = Url.get_or_none(Url.id == url_id)
    if not data:
        return jsonify({"error": "Url not found"}), 404

    data.delete_instance()
    return jsonify({"message": f"Url {url_id} deleted successfully"}), 200

@urls_bp.route("/urls/bulk", methods=["POST"])

def bulk_load_urls():
    import os
    filepath = os.path.join(os.path.dirname(__file__), "..", "..","data", "urls.csv")
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    from app.services.data_loader import load_urls
    from app.database import db
    result = load_urls(filepath)
    if os.environ.get("DATABASE_NAME"):  # postgres only
        db.execute_sql("SELECT setval('urls_id_seq', (SELECT MAX(id) FROM urls))")
    return jsonify({"status": "loaded", "imported": result}), 200

@urls_bp.route("/urls/<string:short_code>/redirect", methods=["GET"])
def redirect_url(short_code):
    url = Url.get_or_none((Url.short_code == short_code) & (Url.is_active == True))
    if not url:
        return jsonify({"error": "not found"}), 404


    details_data = json.dumps(request.headers.get("Referer", ""))

    Event.create(url_id=url.id, user_id=url.user_id, event_type="click", timestamp=datetime.now(timezone.utc), details=details_data)

    from flask import redirect
    return redirect(url.original_url, code=302)
