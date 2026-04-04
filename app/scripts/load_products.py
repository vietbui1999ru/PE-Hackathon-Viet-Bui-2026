from app import create_app
from app.services.data_loader import load_csv

app = create_app()

with app.app_context(filename : str):
    load_csv(filename)
