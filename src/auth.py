import hashlib
import secrets

from src.database import get_connection


def register_user(username, email, password_hash):
    password_hash = hash_password(password_hash)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (username, email, password_hash)
        )

        connection.commit()
        return True

    except Exception:
        return False

    finally:
        connection.close()


def hash_password(password_hash):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac("sha256",
       password_hash.encode("utf-8"),
       salt,
       100_000)
    return salt.hex()+":"+password_hash.hex()

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
            SELECT id, username, email, password_hash, role
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        if verify_password(password, user[3]):
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[4]
            }

        return None

    finally:
        connection.close()