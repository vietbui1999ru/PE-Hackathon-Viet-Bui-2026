import csv
from peewee import chunked
from app.database import db

from app.models import User, Url, Event


def load_model_from_csv(filepath : str, model, unique_columns=None):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            model.insert_many(batch).on_conflict_ignore().execute()

def load_users(filepath: str):
    load_model_from_csv(filepath, User, unique_columns=["id", "username", "email"])

def load_urls(filepath: str):
    load_model_from_csv(filepath, Url, unique_columns=["id", "short_code"])

def load_events(filepath: str):
    load_model_from_csv(filepath, Event, unique_columns=["id"])
