"""
test_auth_integration.py — Integration tests for registration and
login, exercising the REAL endpoint code against a REAL (test) database.
"""


def test_register_creates_user_and_returns_token(client):
    response = client.post("/auth/register", json={
        "email": "integrationtest@example.com",
        "password": "TestPassword123",
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_cannot_register_same_email_twice(client):
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "TestPassword123",
    })

    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "AnotherPassword456",
    })

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_with_correct_credentials_succeeds(client):
    client.post("/auth/register", json={
        "email": "logintest@example.com",
        "password": "CorrectPassword123",
    })

    response = client.post("/auth/login", json={
        "email": "logintest@example.com",
        "password": "CorrectPassword123",
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", json={
        "email": "wrongpasstest@example.com",
        "password": "CorrectPassword123",
    })

    response = client.post("/auth/login", json={
        "email": "wrongpasstest@example.com",
        "password": "WrongPassword999",
    })

    assert response.status_code == 401


def test_login_with_nonexistent_email_fails(client):
    response = client.post("/auth/login", json={
        "email": "doesnotexist@example.com",
        "password": "SomePassword123",
    })

    assert response.status_code == 401


def test_protected_endpoint_rejects_missing_token(client):
    response = client.post("/query/", json={"question": "hello"})
    assert response.status_code in (401, 403)


def test_protected_endpoint_accepts_valid_token(client):
    register_response = client.post("/auth/register", json={
        "email": "protectedtest@example.com",
        "password": "TestPassword123",
    })
    token = register_response.json()["access_token"]

    response = client.post(
        "/query/",
        json={"question": "hello"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code not in (401, 403)
