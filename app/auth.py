import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "auth.db")

app = Flask(__name__)
app.config["SESSION_COOKIE_NAME"] = "auth_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

SESSION_LIFETIME = timedelta(minutes=15)
bcrypt = Bcrypt(app)

limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[])

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_db()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    connection.close()

def valid_username(username):
    return isinstance(username, str) and re.fullmatch(
        r"[A-Za-z0-9_.-]{3,30}", username
    ) is not None

def valid_password(password):
    return isinstance(password, str) and 8 <= len(password) <= 128

def hash_session_token(token):
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(user_id):
    token = secrets.token_urlsafe(32)
    token_hash = hash_session_token(token)
    expires_at = datetime.now(timezone.utc) + SESSION_LIFETIME
    connection = get_db()
    connection.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (token_hash, user_id, expires_at.isoformat())
    )
    connection.commit()
    connection.close()
    return token

def get_authenticated_user():
    token = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
    if not token:
        return None

    token_hash = hash_session_token(token)
    connection = get_db()
    session_record = connection.execute(
        """SELECT sessions.user_id, sessions.expires_at, users.username
           FROM sessions JOIN users ON users.id = sessions.user_id
           WHERE sessions.token_hash = ?""",
        (token_hash,)
    ).fetchone()

    if not session_record:
        connection.close()
        return None

    expires_at = datetime.fromisoformat(session_record["expires_at"])
    if datetime.now(timezone.utc) >= expires_at:
        connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
        connection.commit()
        connection.close()
        return None

    connection.close()
    return {
        "user_id": session_record["user_id"],
        "username": session_record["username"],
        "token_hash": token_hash
    }

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not valid_username(username) or not valid_password(password):
        return jsonify({"error": "Invalid registration data"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    connection = get_db()

    try:
        connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.close()
        return jsonify({"error": "Registration failed"}), 400

    connection.close()
    return jsonify({"message": "Registration successful"}), 201

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid username or password"}), 401

    connection = get_db()
    user = connection.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    connection.close()

    if not user or not bcrypt.check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_session(user["id"])
    response = make_response(jsonify({"message": "Login successful"}))
    response.set_cookie(
        app.config["SESSION_COOKIE_NAME"],
        token,
        httponly=True,
        secure=app.config["SESSION_COOKIE_SECURE"],
        samesite=app.config["SESSION_COOKIE_SAMESITE"],
        max_age=int(SESSION_LIFETIME.total_seconds())
    )
    return response, 200

@app.route("/profile", methods=["GET"])
def profile():
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Authentication required"}), 401
    return jsonify({"username": user["username"], "authenticated": True}), 200

@app.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
    if token:
        token_hash = hash_session_token(token)
        connection = get_db()
        connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
        connection.commit()
        connection.close()

    response = make_response(jsonify({"message": "Logged out"}))
    response.delete_cookie(app.config["SESSION_COOKIE_NAME"])
    return response, 200

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
