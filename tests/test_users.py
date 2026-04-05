# tests/test_users.py
from app.models.users import User

def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data

def test_list_users_pagination(client):
    response = client.get("/users?page=1&per_page=10")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) <= 10

def test_create_user(client):
    response = client.post("/users", json={
        "username": "testuser",
        "email": "testuser@example.com"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    User.delete().where(User.username == "testuser").execute()

def test_create_user_duplicate(client):
    client.post("/users", json={"username": "dupuser", "email": "dup@example.com"})
    response = client.post("/users", json={"username": "dupuser", "email": "dup@example.com"})
    assert response.status_code == 409
    User.delete().where(User.username == "dupuser").execute()

def test_create_user_missing_fields(client):
    response = client.post("/users", json={"username": "onlyusername"})
    assert response.status_code == 400

def test_get_user(client):
    user = User.create(username="getuser", email="getuser@example.com")
    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == user.id
    user.delete_instance()

def test_get_user_not_found(client):
    response = client.get("/users/99999")
    assert response.status_code == 404

def test_update_user(client):
    user = User.create(username="updateuser", email="update@example.com")
    response = client.put(f"/users/{user.id}", json={"username": "updateduser"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "updateduser"
    user.delete_instance()

def test_delete_user(client):
    user = User.create(username="deleteuser", email="delete@example.com")
    response = client.delete(f"/users/{user.id}")
    assert response.status_code == 200
    assert User.get_or_none(User.id == user.id) is None

def test_delete_user_not_found(client):
    response = client.delete("/users/99999")
    assert response.status_code == 404
