import csv
from peewee import chunked
from app.database import db
from app.models.product import Product

def load_csv(filepath : str):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            Product.insert_many(batch).execute()
