import pytest
from app import create_app

@pytest.fixture()

def app():
    """App for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        })
    yield app

@pytest.fixture()
def client(app):
    """Test client for app."""
    return app.test_client()
