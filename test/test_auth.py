import src.database as database
from src.auth import (
    hash_password,
    verify_password,
    register_user,
    login_user
)
from src.database import create_users_table


def test_password_hashing():
    password = "test123"

    stored_hash = hash_password(password)

    assert stored_hash != password
    assert verify_password(password, stored_hash)
    assert not verify_password("wrongpassword", stored_hash)


def test_register_user(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    create_users_table()

    result = register_user(
        "newuser",
        "newuser@example.com",
        "password123"
    )

    assert result is True

def test_duplicate_username_or_email(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    create_users_table()

    first = register_user(
        "fareed",
        "fareed@example.com",
        "password123"
    )

    second = register_user(
        "fareed",
        "another@example.com",
        "password456"
    )

    assert first is True
    assert second is False    

def test_login_user(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    create_users_table()

    register_user(
        "loginuser",
        "login@example.com",
        "password123"
    )

    correct_login = login_user("loginuser", "password123")
    wrong_login = login_user("loginuser", "wrongpassword")

    assert correct_login is not None
    assert correct_login["username"] == "loginuser"
    assert wrong_login is None    