import hashlib
import hmac
import secrets
from contextlib import closing

import psycopg

from src.database import configured_admin_emails, get_connection

ITERATIONS = 600_000
VALID_ROLES = ("landlord", "tenant")


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_hash):
    try:
        if stored_hash.count("$") == 3:
            _, iters, salt_hex, hash_hex = stored_hash.split("$")
            iterations = int(iters)
        else:
            salt_hex, hash_hex = stored_hash.split(":")
            iterations = 100_000
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected)


def register_user(username, email, password, role="tenant", full_name=None, phone="0241234567"):
    if not all(isinstance(value, str) for value in (username, email, password)):
        return False
    username = (username or "").strip()
    email = (email or "").strip().lower()
    role = str(role).strip().lower() if role else "tenant"
    if role not in VALID_ROLES:
        return False

    if not username or not email or len(password) < 8:
        return False

    stored_role = "admin" if email in configured_admin_emails() else role

    connection = get_connection()
    try:
        exists = connection.execute(
            "SELECT 1 FROM users WHERE lower(username) = lower(%s) OR lower(email) = %s",
            (username, email),
        ).fetchone()
        if exists:
            return False

        connection.execute(
            """
            INSERT INTO users (username, email, password_hash, role, full_name, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (username, email, hash_password(password), stored_role, (full_name or username).strip(), (phone or "0241234567").strip()),
        )
        connection.commit()
        return True

    except psycopg.errors.UniqueViolation:
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
            SELECT id, username, email, password_hash, role, full_name, phone, show_whatsapp, show_phone
            FROM users
            WHERE lower(username) = lower(%s) OR lower(email) = lower(%s)
            """,
            (username, username),
        ).fetchone()

        if user is None or not verify_password(password, user["password_hash"]):
            return None

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"] or user["username"],
            "phone": user.get("phone") or "0241234567",
            "show_whatsapp": user.get("show_whatsapp") if user.get("show_whatsapp") is not None else True,
            "show_phone": user.get("show_phone") if user.get("show_phone") is not None else True,
        }

    finally:
        connection.close()


def get_user_by_id(user_id):
    if not user_id:
        return None
    with closing(get_connection()) as connection, connection:
        user = connection.execute(
            """
            SELECT id, username, email, role, full_name, phone, show_whatsapp, show_phone, created_at
            FROM users
            WHERE id = %s
            """,
            (int(user_id),),
        ).fetchone()
        if not user:
            return None
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"] or user["username"],
            "phone": user.get("phone") or "0241234567",
            "show_whatsapp": user.get("show_whatsapp") if user.get("show_whatsapp") is not None else True,
            "show_phone": user.get("show_phone") if user.get("show_phone") is not None else True,
        }


def update_user_profile(user_id, full_name=None, phone=None, show_whatsapp=None, show_phone=None):
    if not user_id:
        return None
    with closing(get_connection()) as connection, connection:
        updates = []
        params = []
        if full_name is not None:
            updates.append("full_name = %s")
            params.append(str(full_name).strip())
        if phone is not None:
            updates.append("phone = %s")
            params.append(str(phone).strip())
        if show_whatsapp is not None:
            updates.append("show_whatsapp = %s")
            params.append(bool(show_whatsapp))
        if show_phone is not None:
            updates.append("show_phone = %s")
            params.append(bool(show_phone))

        if not updates:
            return get_user_by_id(user_id)

        params.append(int(user_id))
        connection.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", params)
        return get_user_by_id(user_id)
