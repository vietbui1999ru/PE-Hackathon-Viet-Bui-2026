from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.urls import Url

urls_bp = Blueprint("urls", __name__)


@urls_bp.route("/urls")
def list_urls():
    # add pagination later
    urls = Url.select()
    # model_to_dict return controlled fields for each u in users
    return jsonify({"data" : [model_to_dict(only=[Url.id, Url.username, Url.email]) for u in urls]})
