import csv
from peewee import chunked
from app.database import db

from app.models import User, Url, Event

def validate_unique_column(rows, column_name: str, filepath: str):
    seen = set()
    duplicates = set()

    for row in rows:
        value = row.get(column_name)
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    if duplicates:
        dupes = ", ".join(sorted(duplicates))
        raise ValueError(
            f"Duplicate {column_name} values found in {filepath}: {dupes}"
        )

def load_model_from_csv(filepath : str, model, unique_columns=None):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if unique_columns:
        for column in unique_columns:
            validate_unique_column(rows, column, filepath)

    with db.atomic():
        for batch in chunked(rows, 100):
            model.insert_many(batch).execute()

def load_users(filepath: str):
    load_model_from_csv(filepath, User, unique_columns=["id", "username", "email"])

def load_urls(filepath: str):
    load_model_from_csv(filepath, Url, unique_columns=["id", "short_code"])

def load_events(filepath: str):
    load_model_from_csv(filepath, Event, unique_columns=["id"])
