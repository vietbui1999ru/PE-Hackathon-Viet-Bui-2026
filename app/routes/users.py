from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.users import User

users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
def list_users():
    # add pagination later
    users = User.select()
    # model_to_dict return controlled fields for each u in users
    return jsonify({"data" : [model_to_dict(only=[User.id, User.username, User.email]) for u in users]})
