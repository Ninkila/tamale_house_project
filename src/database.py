import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "tamale_house.db"
CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "tamale_house_rentals.csv"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'tenant',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Properties Table
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

    # Favourites Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            house_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES users(id),
            FOREIGN KEY (house_id) REFERENCES properties(house_id)
        )
    """)

    # Enquiries Table
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    seed_properties_if_empty(connection)
    connection.close()


def seed_properties_if_empty(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM properties")
    count = cursor.fetchone()[0]

    if count == 0 and CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO properties (
                    house_id, neighborhood, house_type, rooms, bathrooms,
                    furnishing, distance_from_central_tamale_km, electricity,
                    water, compound, monthly_rent_ghs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('house_id'), row.get('neighborhood'), row.get('house_type'),
                int(row.get('rooms', 1)), int(row.get('bathrooms', 1)),
                row.get('furnishing'), float(row.get('distance_from_central_tamale_km', 5.0)),
                row.get('electricity'), row.get('water'), row.get('compound'),
                float(row.get('monthly_rent_ghs', 0))
            ))
        connection.commit()