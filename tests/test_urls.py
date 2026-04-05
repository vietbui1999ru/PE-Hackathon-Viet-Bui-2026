# tests/test_urls.py
import uuid
from app.models.urls import Url
from app.models.events import Event

def test_list_urls(client):
    response = client.get("/urls")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data

def test_list_urls_by_user(client):
    response = client.get("/urls?user_id=1")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    for url in data["data"]:
        assert url["user_id"] == 1

def test_list_urls_active_only(client):
    response = client.get("/urls?is_active=true")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    for url in data["data"]:
        assert url["is_active"] == True

def test_create_url(client):
    response = client.post("/urls", json={
        "original_url": "https://example.com/test",
        "title": "Test URL",
        "user_id": 1
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/test"
    Url.delete().where(Url.short_code == data["short_code"]).execute()

def test_create_url_missing_fields(client):
    response = client.post("/urls", json={"title": "No URL"})
    assert response.status_code == 400

def test_create_url_invalid_url(client):
    response = client.post("/urls", json={
        "original_url": "not-a-url",
        "user_id": 1
    })
    assert response.status_code == 400

def test_create_url_duplicate_short_code(client):
    short_code = uuid.uuid4().hex[:8]
    client.post("/urls", json={
        "original_url": "https://example.com/first",
        "user_id": 1,
        "short_code": short_code
    })
    response = client.post("/urls", json={
        "original_url": "https://example.com/second",
        "user_id": 1,
        "short_code": short_code
    })
    assert response.status_code == 409
    Url.delete().where(Url.short_code == short_code).execute()

def test_get_url_by_id(client):
    url = Url.create(
        original_url="https://example.com/get",
        title="Get Test",
        user_id=1,
        short_code=uuid.uuid4().hex[:8]
    )
    response = client.get(f"/urls/{url.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == url.id
    url.delete_instance()

def test_get_url_not_found(client):
    response = client.get("/urls/99999")
    assert response.status_code == 404

def test_update_url(client):
    url = Url.create(
        original_url="https://example.com/update",
        title="Before",
        user_id=1,
        short_code=uuid.uuid4().hex[:8]
    )
    response = client.put(f"/urls/{url.id}", json={"title": "After"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "After"
    url.delete_instance()

def test_deactivate_url(client):
    url = Url.create(
        original_url="https://example.com/deactivate",
        title="Active",
        user_id=1,
        short_code=uuid.uuid4().hex[:8],
        is_active=True
    )
    response = client.put(f"/urls/{url.id}", json={"is_active": False})
