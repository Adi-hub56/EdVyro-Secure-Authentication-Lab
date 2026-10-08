import pytest
from app import auth

@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(auth, "DATABASE", str(test_db))
    auth.app.config.update(TESTING=True)
    auth.init_db()
    auth.limiter.reset()
    with auth.app.test_client() as client:
        yield client

def register_user(client):
    return client.post("/register", json={
        "username": "testuser",
        "password": "TestPassword123!"
    })

def login_user(client):
    return client.post("/login", json={
        "username": "testuser",
        "password": "TestPassword123!"
    })

def test_registration(client):
    response = register_user(client)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Registration successful"

def test_password_is_hashed(client):
    register_user(client)
    connection = auth.get_db()
    user = connection.execute(
        "SELECT password_hash FROM users WHERE username = ?", ("testuser",)
    ).fetchone()
    connection.close()
    assert user is not None
    assert user["password_hash"] != "TestPassword123!"
    assert user["password_hash"].startswith("$2")

def test_successful_login(client):
    register_user(client)
    response = login_user(client)
    assert response.status_code == 200
    cookie = response.headers.get("Set-Cookie")
    assert "auth_session=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Max-Age=900" in cookie

def test_wrong_password_returns_generic_error(client):
    register_user(client)
    response = client.post("/login", json={
        "username": "testuser",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"

def test_profile_requires_authentication(client):
    response = client.get("/profile")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"

def test_authenticated_profile(client):
    register_user(client)
    login_response = login_user(client)
    cookie = login_response.headers["Set-Cookie"].split(";", 1)[0]
    response = client.get("/profile", headers={"Cookie": cookie})
    assert response.status_code == 200
    assert response.get_json()["authenticated"] is True
    assert response.get_json()["username"] == "testuser"

def test_logout_revokes_session(client):
    register_user(client)
    login_response = login_user(client)
    cookie = login_response.headers["Set-Cookie"].split(";", 1)[0]
    logout_response = client.post("/logout", headers={"Cookie": cookie})
    assert logout_response.status_code == 200
    replay_response = client.get("/profile", headers={"Cookie": cookie})
    assert replay_response.status_code == 401
    assert replay_response.get_json()["error"] == "Authentication required"

def test_rate_limiting(client):
    register_user(client)
    responses = []
    for _ in range(6):
        response = client.post("/login", json={
            "username": "testuser",
            "password": "WrongPassword!"
        })
        responses.append(response.status_code)
    assert responses[:5] == [401, 401, 401, 401, 401]
    assert responses[5] == 429
