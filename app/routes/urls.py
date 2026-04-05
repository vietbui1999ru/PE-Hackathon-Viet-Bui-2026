from flask.globals import request
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.urls import Url

urls_bp = Blueprint("urls", __name__)


@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    # add pagination later
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)
    urls = Url.select()
    if page and per_page:
        urls = urls.paginate(page, per_page)
    # model_to_dict return controlled fields for each u in users
    return jsonify({"data" : [model_to_dict(u) for u in urls]})

@urls_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "url is required"}), 400

    url = Url.create(url=data["url"])
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
    if "url" in update_data:
        data.url = update_data["url"]

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
    data = request.get_json()
    import os
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "urls.csv")
    if not filepath:
        return jsonify({"error": "File not found"}), 404
    from app.services.data_loader import load_urls
    load_urls(filepath)
    return jsonify({"status": "loaded"}), 201
