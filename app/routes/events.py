from datetime import datetime, timezone
from flask.globals import request
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.events import Event

import json

events_bp = Blueprint("events", __name__)


@events_bp.route("/events")
def list_events():
    events = Event.select()

    if request.args.get("user_id"):
        user_id = request.args.get("user_id")
        events = events.where(Event.user_id == int(user_id))

    if request.args.get("url_id"):
        url_id = request.args.get("url_id")
        events = events.where(Event.url_id == int(url_id))

    if request.args.get("event_type"):
        event_type = request.args.get("event_type")
        events = events.where(Event.event_type == event_type)
    # model_to_dict return controlled fields for each e in events
    return jsonify({"data" : [model_to_dict(e) for e in events]})

@events_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    if not data or "url_id" not in data or "user_id" not in data or "event_type" not in data:
        return jsonify({"error": "Missing required fields for url_id, user_id, and event_type"}), 400
    try:
        url_id = int(data["url_id"])
        user_id = int(data["user_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "url_id and user_id must be integers"}), 400

    details_data = json.dumps(data.get("details", {}))
    try:
        event = Event.create(url_id=url_id, user_id=user_id, event_type=data["event_type"], timestamp=datetime.now(timezone.utc), details=details_data)
    except IntegrityError:
        return jsonify({"error": "Event already exists"}), 409
    return jsonify(model_to_dict(event)), 201

@events_bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    data = Event.get_or_none(Event.id == event_id)
    if not data:
        return jsonify({"error": "Event not found"}), 404

    return jsonify(model_to_dict(data)), 200

@events_bp.route("/events/<int:event_id>", methods=["PUT"])

def update_event(event_id):
    data = Event.get_or_none(Event.id == event_id)
    if not data:
        return jsonify({"error": "Event not found"}), 404

    update_data = request.get_json()
    if "url_id" in update_data:
        data.url_id = update_data["url_id"]
    if "user_id" in update_data:
        data.user_id = update_data["user_id"]
    if "event_type" in update_data:
        data.event_type = update_data["event_type"]
    if "timestamp" in update_data:
        data.timestamp = update_data["timestamp"]
    if "details" in update_data:
        data.details = update_data["details"]

    data.save()
    return jsonify(model_to_dict(data)), 200

@events_bp.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    data = Event.get_or_none(Event.id == event_id)
    if not data:
        return jsonify({"error": "Event not found"}), 404

    data.delete_instance()
    return jsonify({"message": f"Event {event_id} deleted successfully"}), 200

@events_bp.route("/events/bulk", methods=["POST"])
def bulk_load_events():
    import os
    filepath = os.path.join(os.path.dirname(__file__), ".." , "..", "data", "events.csv")
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    from app.services.data_loader import load_events
    from app.database import db
    result = load_events(filepath)
    if os.environ.get("DATABASE_NAME"):  # postgres only
        db.execute_sql("SELECT setval('events_id_seq', (SELECT MAX(id) FROM events))")
    return jsonify({"status": "loaded", "imported": result}), 200
