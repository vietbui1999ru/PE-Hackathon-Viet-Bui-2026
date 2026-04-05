def test_create_url(client):
    response = client.post("/urls", json={"original_url": "https://example.com/some-url", "title" : "Test Create Url", "user_id" : 1
                                          })

    assert response.status_code == 201

    data = response.get_json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/some-url"

    from app.models import Url
    Url.delete().where(Url.short_code == data["short_code"], Url.user_id == 1).execute()

