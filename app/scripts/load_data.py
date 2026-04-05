from app import create_app
from app.services.data_loader import load_users, load_urls, load_events

def main():

    app = create_app()
    with app.app_context():
        load_users("data/users.csv")
        load_urls("data/urls.csv")
        load_events("data/events.csv")

if __name__ == "__main__":
    main()
