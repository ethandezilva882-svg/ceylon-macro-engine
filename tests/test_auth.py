CREDS = {"email": "user@example.com", "password": "testpassword123"}


def test_register_returns_token_and_user(client):
    res = client.post("/api/auth/register", json=CREDS)
    assert res.status_code == 201
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == CREDS["email"]
    assert "hashed_password" not in body["user"]


def test_register_duplicate_email_rejected(client):
    client.post("/api/auth/register", json=CREDS)
    res = client.post("/api/auth/register", json=CREDS)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_register_short_password_rejected(client):
    res = client.post("/api/auth/register", json={"email": "a@b.com", "password": "short"})
    assert res.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json=CREDS)
    res = client.post("/api/auth/login", json=CREDS)
    assert res.status_code == 200
    assert res.json()["access_token"]


def test_login_wrong_password(client):
    client.post("/api/auth/register", json=CREDS)
    res = client.post("/api/auth/login", json={**CREDS, "password": "wrongpassword"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Incorrect email or password"


def test_login_unknown_email_same_error(client):
    res = client.post("/api/auth/login", json=CREDS)
    assert res.status_code == 401
    assert res.json()["detail"] == "Incorrect email or password"


def test_protected_route_without_token(client):
    assert client.get("/api/basket").status_code == 401


def test_protected_route_with_tampered_token(client, auth_headers):
    bad = {"Authorization": auth_headers["Authorization"][:-4] + "abcd"}
    assert client.get("/api/basket", headers=bad).status_code == 401


def test_protected_route_with_garbage_token(client):
    res = client.get("/api/basket", headers={"Authorization": "Bearer garbage.token.here"})
    assert res.status_code == 401
