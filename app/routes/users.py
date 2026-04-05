from flask.globals import request
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.users import User

users_bp = Blueprint("users", __name__)


"""
List all users
"""
@users_bp.route("/users", methods=["GET"])
def list_users():
    # add pagination later
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)
    users_query = User.select()
    if page and per_page:
        users_query = users_query.paginate(page, per_page)
    # model_to_dict return controlled fields for each u in users
    return jsonify({"data" : [model_to_dict(u) for u in users_query]})

"""
Create new user
"""
@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "username" not in data or "email" not in data:
        return jsonify({"error": "username and email are required"}), 400

    user = User.create(username=data["username"], email=data["email"])
    return jsonify(model_to_dict(user, only=[User.id, User.username, User.email, User.created_at])), 201

"""
get unique user by id
"""
@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    data = User.get_or_none(User.id == user_id)
    if not data:
        return jsonify({"error": "User not found"}), 404

    return jsonify(model_to_dict(data, only=[User.id, User.username, User.email, User.created_at])), 200

"""
update user by id
"""
@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = User.get_or_none(User.id == user_id)
    if not data:
        return jsonify({"error": "User not found"}), 404

    update_data = request.get_json()
    if "username" in update_data:
        data.username = update_data["username"]
    if "email" in update_data:
        data.email = update_data["email"]

    data.save()
    return jsonify(model_to_dict(data, only=[User.id, User.username, User.email, User.created_at])), 200

@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    data = User.get_or_none(User.id == user_id)
    if not data:
        return jsonify({"error": "User not found"}), 404

    data.delete_instance()
    return jsonify({"message": f"User {user_id} deleted successfully"}), 200

@users_bp.route("/users/bulk", methods=["POST"])

def bulk_load_users():
    import os
    filepath = os.path.join(os.path.dirname(__file__), "..", "..", "data", "users.csv")
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    from app.services.data_loader import load_users
    from app.database import db
    load_users(filepath)
    db.execute_sql("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
    return jsonify({"status": "loaded"}), 200
