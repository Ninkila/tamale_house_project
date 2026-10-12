import argparse
import sqlite3
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "data" / "tamale_house.db"
CSV_PATH = REPO_ROOT / "data" / "tamale_house_rentals.csv"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _ensure_user_table_schema(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                full_name TEXT,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('landlord', 'tenant')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        return

    columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
    if "full_name" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    if "password_hash" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "role" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'tenant'")
    if "created_at" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")


def create_users_table():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        _ensure_user_table_schema(connection)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                house_id TEXT PRIMARY KEY,
                neighborhood TEXT NOT NULL,
                house_type TEXT NOT NULL,
                rooms INTEGER NOT NULL,
                bathrooms INTEGER NOT NULL,
                furnishing TEXT,
                distance_from_central_tamale_km REAL,
                electricity TEXT,
                water TEXT,
                compound TEXT,
                monthly_rent_ghs REAL NOT NULL,
                landlord_id INTEGER,
                landlord_phone TEXT DEFAULT '0241234567',
                show_whatsapp INTEGER DEFAULT 1,
                show_phone INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (landlord_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favourites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                house_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (tenant_id, house_id),
                FOREIGN KEY (tenant_id) REFERENCES users(id),
                FOREIGN KEY (house_id) REFERENCES properties(house_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id TEXT NOT NULL,
                tenant_id INTEGER,
                landlord_id INTEGER,
                tenant_name TEXT NOT NULL,
                tenant_email TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(house_id),
                FOREIGN KEY (tenant_id) REFERENCES users(id),
                FOREIGN KEY (landlord_id) REFERENCES users(id)
            )
        """)

        connection.commit()
        seed_properties_if_empty(connection)
    finally:
        connection.close()


def _num(value, default, cast):
    try:
        if pd.isna(value):
            return default
        return cast(value)
    except (TypeError, ValueError):
        return default


def seed_properties_if_empty(connection):
    cursor = connection.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM properties").fetchone()[0]

    if count or not CSV_PATH.exists():
        return

    df = pd.read_csv(CSV_PATH)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO properties (
                house_id, neighborhood, house_type, rooms, bathrooms,
                furnishing, distance_from_central_tamale_km, electricity,
                water, compound, monthly_rent_ghs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("house_id"), row.get("neighborhood"), row.get("house_type"),
            _num(row.get("rooms"), 1, int), _num(row.get("bathrooms"), 1, int),
            row.get("furnishing"),
            _num(row.get("distance_from_central_tamale_km"), 5.0, float),
            row.get("electricity"), row.get("water"), row.get("compound"),
            _num(row.get("monthly_rent_ghs"), 0.0, float),
        ))
    connection.commit()


def delete_all_users(confirm=False):
    """Delete every user and all data that belongs to them (one transaction).

    Removes: favourites, enquiries, and listings owned by a user.
    Keeps: seeded (unowned) listings. Resets ID counters.
    """
    if not confirm:
        raise ValueError("Refusing to delete users without confirm=True")

    create_users_table()  # make sure tables exist
    connection = get_connection()
    try:
        with connection:  # commits on success, rolls back on error
            connection.execute("DELETE FROM favourites")
            connection.execute("DELETE FROM enquiries")
            connection.execute("DELETE FROM properties WHERE landlord_id IS NOT NULL")
            deleted = connection.execute("DELETE FROM users").rowcount
            connection.execute(
                "DELETE FROM sqlite_sequence WHERE name IN ('users', 'favourites', 'enquiries')"
            )
        return deleted
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete all users and their data.")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args()

    if args.yes or input("Type DELETE to remove ALL users and their data: ").strip() == "DELETE":
        print(f"Deleted {delete_all_users(confirm=True)} user(s).")
    else:
        print("Cancelled.")
