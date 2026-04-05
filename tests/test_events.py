from app.models.events import Event
def test_get_events_list(client):
    response = client.get("/events")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data

def test_get_events_by_url(client):
    response = client.get("/events?url_id=1")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    for event in data["data"]:
        assert event["url_id"] == 1

def test_get_events_by_user(client):
    response = client.get("/events?user_id=1")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    for event in data["data"]:
        assert event["user_id"] == 1

def test_get_events_by_type(client):
    response = client.get("/events?event_type=click")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    for event in data["data"]:
        assert event["event_type"] == "click"

def test_create_event(client):
    response = client.post("/events", json={
        "url_id": 1,
        "user_id": 1,
        "event_type": "click",
        "details": {"referrer": "https://google.com"}
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["event_type"] == "click"
    assert data["url_id"] == 1

def test_create_event_missing_fields(client):
    response = client.post("/events", json={"url_id": 1})
    assert response.status_code == 400
