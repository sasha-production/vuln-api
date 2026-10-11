def test_create_and_list_notes(client, auth_headers):
    r = client.post(
        "/notes",
        json={"title": "hello", "body": "world"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    note = r.json()
    assert note["title"] == "hello"
    assert note["owner_id"] == 1

    r = client.get("/notes", headers=auth_headers)
    assert r.status_code == 200
    ids = [n["id"] for n in r.json()]
    assert note["id"] in ids


def test_get_note_by_id(client, auth_headers):
    r = client.post("/notes", json={"title": "t", "body": "b"}, headers=auth_headers)
    note_id = r.json()["id"]

    r = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["title"] == "t"


def test_update_note(client, auth_headers):
    r = client.post("/notes", json={"title": "old", "body": "b"}, headers=auth_headers)
    note_id = r.json()["id"]

    r = client.put(
        f"/notes/{note_id}",
        json={"title": "new"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "new"
    assert r.json()["body"] == "b"


def test_delete_note(client, auth_headers):
    r = client.post("/notes", json={"title": "x", "body": "y"}, headers=auth_headers)
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert r.status_code == 200

    r = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert r.status_code == 404
