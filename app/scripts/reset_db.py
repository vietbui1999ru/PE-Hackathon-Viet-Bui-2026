from app import create_app
from app.database import db


"""
Reset script for when want to test manual or automate
"""
def main():
    app = create_app()

    with app.app_context():
        db.connect(reuse_if_open=True)
        db.execute_sql("TRUNCATE TABLE events, urls, users RESTART IDENTITY CASCADE;")
        db.close()


if __name__ == "__main__":
    main()
