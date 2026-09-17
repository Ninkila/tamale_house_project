import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1]/"data"/"tamale_house.db"


def get_connection():
    return sqlite3.connect(DB_PATH)

def create_users_table():
    connection = get_connection()
    connection.execute("""
       CREATE TABLE IF NOT EXISTS users(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT NOT NULL UNIQUE,
       email TEXT NOT NULL UNIQUE,
       password_hash TEXT NOT NULL,
       role TEXT NOT NULL DEFAULT "user")

    """)
    connection.commit()
    connection.close()