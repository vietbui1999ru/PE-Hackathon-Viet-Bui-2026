import datetime
from datetime import timezone
from flask.globals import request
from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.events import Event

events_bp = Blueprint("events", __name__)


@events_bp.route("/events")
def list_events():
    # add pagination later
    pages = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)

    events = Event.select()
    if pages and per_page:
        events = events.paginate(pages, per_page)
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

    event = Event.create(url_id=url_id, user_id=user_id, event_type=data["event_type"], timestamp=datetime.now(timezone.utc), details=str(data.get("details", "")))
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
    load_events(filepath)
    db.execute_sql("SELECT setval('events_id_seq', (SELECT MAX(id) FROM events))")
    return jsonify({"status": "loaded"}), 200
