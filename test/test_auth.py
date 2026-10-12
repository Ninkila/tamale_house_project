import os
import uuid
from contextlib import closing

import pytest

from src.auth import hash_password, login_user, register_user, verify_password
from src.database import create_users_table, get_connection

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
requires_postgres = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to run PostgreSQL authentication integration tests.",
)


@pytest.fixture
def postgres_db(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    create_users_table()


def test_password_hashing():
    password = "test123"
    stored_hash = hash_password(password)

    assert stored_hash != password
    assert verify_password(password, stored_hash)
    assert not verify_password("wrongpassword", stored_hash)


def test_registration_returns_actionable_error_without_postgres(monkeypatch):
    import src.database as database

    def unavailable_database():
        raise RuntimeError("Set DATABASE_URL to a PostgreSQL connection string.")

    monkeypatch.setattr(database, "create_users_table", unavailable_database)
    import server

    monkeypatch.setattr(server, "create_users_table", unavailable_database)
    monkeypatch.setattr(server, "DATABASE_READY", False)
    response = server.app.test_client().post(
        "/api/auth/register",
        json={
            "username": "new-user",
            "email": "new-user@example.com",
            "password": "password123",
            "role": "tenant",
        },
    )

    assert response.status_code == 503
    assert "DATABASE_URL" in response.get_json()["error"]


@requires_postgres
def test_register_and_login(postgres_db):
    suffix = uuid.uuid4().hex
    username = f"test_{suffix}"
    email = f"{username}@example.com"

    assert register_user(username, email, "password123", "tenant") is True
    user = login_user(email.upper(), "password123")
    assert user["username"] == username
    assert user["role"] == "tenant"
    assert login_user(username, "wrongpassword") is None

    with closing(get_connection()) as connection, connection:
        connection.execute("DELETE FROM users WHERE username = %s", (username,))


@requires_postgres
def test_duplicate_username_or_email_is_rejected(postgres_db):
    suffix = uuid.uuid4().hex
    username = f"test_{suffix}"
    email = f"{username}@example.com"

    assert register_user(username, email, "password123") is True
    assert register_user(username.upper(), f"other_{suffix}@example.com", "password456") is False
    assert register_user(f"other_{suffix}", email.upper(), "password456") is False

    with closing(get_connection()) as connection, connection:
        connection.execute("DELETE FROM users WHERE username = %s", (username,))
