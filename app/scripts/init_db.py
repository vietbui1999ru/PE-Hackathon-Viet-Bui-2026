from app import create_app
from app.database import db
from app.models import User, Event, Url

def main():
    app = create_app()

    with app.app_context():
        db.connect(reuse_if_open=True)
        db.create_tables([User, Event, Url], safe=True)
        db.close()
if __name__ == "__main__":
    main()
