import hashlib
import hmac
import secrets
import sqlite3

from src.database import get_connection

ITERATIONS = 600_000
VALID_ROLES = ("landlord", "tenant")


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_hash):
    try:
        if stored_hash.count("$") == 3:  # current format
            _, iters, salt_hex, hash_hex = stored_hash.split("$")
            iterations = int(iters)
        else:  # legacy "salt:hash" format
            salt_hex, hash_hex = stored_hash.split(":")
            iterations = 100_000
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected)


def register_user(username, email, password, role="tenant", full_name=None):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    role = str(role).strip().lower() if role else "tenant"
    if role not in VALID_ROLES:
        role = "tenant"

    if not username or not email or not password:
        return False

    connection = get_connection()
    try:
        exists = connection.execute(
            "SELECT 1 FROM users WHERE lower(username) = lower(?) OR lower(email) = ?",
            (username, email),
        ).fetchone()
        if exists:
            return False

        connection.execute(
            """
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, email, hash_password(password), role, (full_name or username).strip()),
        )
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def login_user(username, password):
    username = (username or "").strip()
    if not username or not password:
        return None

    connection = get_connection()
    try:
        user = connection.execute(
            """
            SELECT id, username, email, password_hash, role, full_name
            FROM users
            WHERE lower(username) = lower(?) OR lower(email) = lower(?)
            """,
            (username, username),
        ).fetchone()

        if user is None or not verify_password(password, user[3]):
            return None

        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[4],
            "full_name": user[5] or user[1],
        }

    finally:
        connection.close()
