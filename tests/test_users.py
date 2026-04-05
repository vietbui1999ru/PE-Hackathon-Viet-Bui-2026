def test_get_users_list(client):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data

