import hashlib
import secrets

from src.database import get_connection


def register_user(username, email, password_hash, role="tenant", full_name=None):
    # Ensure role is explicitly landlord or tenant
    assigned_role = str(role).lower() if role else "tenant"
    if assigned_role not in ("landlord", "tenant"):
        assigned_role = "tenant"

    password_hash_str = hash_password(password_hash)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, email, password_hash_str, assigned_role, full_name or username)
        )

        connection.commit()
        return True

    except Exception:
        return False

    finally:
        connection.close()


def hash_password(password_hash):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password_hash.encode("utf-8"),
        salt,
        100_000
    )
    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_hash):
    salt_hex, hash_hex = stored_hash.split(":")

    salt = bytes.fromhex(salt_hex)
    stored_password_hash = bytes.fromhex(hash_hex)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000
    )

    return secrets.compare_digest(password_hash, stored_password_hash)


def login_user(username, password):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT id, username, email, password_hash, role, full_name
            FROM users
            WHERE username = ? OR email = ?
            """,
            (username, username)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        if verify_password(password, user[3]):
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[4],
                "full_name": user[5] if len(user) > 5 and user[5] else user[1]
            }

        return None

    finally:
        connection.close()