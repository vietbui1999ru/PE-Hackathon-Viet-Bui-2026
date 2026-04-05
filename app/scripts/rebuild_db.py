from app import create_app
from app.database import db
from app.models import User, Url, Event


def main():
    app = create_app()

    with app.app_context():
        db.connect(reuse_if_open=True)
        db.drop_tables([Event, Url, User], safe=True)
        db.create_tables([User, Url, Event], safe=True)
        db.close()


if __name__ == "__main__":
    main()
