from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.events import Event

events_bp = Blueprint("events", __name__)


@events_bp.route("/events")
def list_events():
    # add pagination later
    events = Event.select()
    # model_to_dict return controlled fields for each e in events
    return jsonify({"data" : [model_to_dict(only=[Event.url_id, Event.user_id, Event.event_type]) for e in events]})
