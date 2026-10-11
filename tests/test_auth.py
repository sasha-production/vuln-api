def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_register_and_login(client):
    r = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "qwerty123"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["username"] == "bob"
    assert body["email"] == "bob@example.com"
    assert "password" not in body and "password_hash" not in body

    r = client.post(
        "/auth/login",
        json={"username": "bob", "email": "bob@example.com", "password": "qwerty123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    r = client.post(
        "/auth/login",
        json={"username": "alice", "email": "alice@example.com", "password": "wrong"},
    )
    assert r.status_code == 422


def test_me_requires_auth(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_me_with_token(client, auth_headers):
    r = client.get("/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "alice"
