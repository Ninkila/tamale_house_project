import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from src.database import create_users_table, get_connection
from src.auth import register_user, login_user
from src.house_search import find_houses

app = Flask(__name__, static_folder="frontend", static_url_path="")

# Ensure database tables exist
create_users_table()


# --- SERVE FRONTEND STATIC FILES ---
@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    target = Path("frontend") / path
    if target.exists():
        return send_from_directory("frontend", path)
    return send_from_directory("frontend", "index.html")


# --- REST API ENDPOINTS ---

# 1. Browse & Search Houses
@app.route("/api/houses", methods=["GET"])
def get_houses():
    budget = float(request.args.get("budget", 999999))
    location = request.args.get("neighborhood", request.args.get("location", ""))
    bedroom = int(request.args.get("bedroom", request.args.get("rooms", 0)))
    water = request.args.get("water", "Any")
    bathroom = int(request.args.get("bathroom", request.args.get("bathrooms", 0)))

    try:
        df = find_houses(budget, location, bedroom, water, bathroom)
        houses = df.to_dict(orient="records")
        return jsonify(houses)
    except Exception as e:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM properties")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(rows)


# 2. Get Single Property Details
@app.route("/api/houses/<house_id>", methods=["GET"])
def get_house_detail(house_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE house_id = ?", (house_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Property not found"}), 404


# 3. User Authentication
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.json or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "").strip().lower()
    full_name = data.get("full_name", "").strip()

    if not username or not email or not password or not role:
        return jsonify({"error": "Missing required fields. Please specify your account role (Landlord or Tenant)."}), 400

    if role not in ["landlord", "tenant"]:
        return jsonify({"error": "Invalid role specified. Role must be 'landlord' or 'tenant'."}), 400

    success = register_user(username, email, password, role=role, full_name=full_name)
    if success:
        return jsonify({
            "message": "User registered successfully",
            "user": {"username": username, "email": email, "role": role, "full_name": full_name or username}
        })
    return jsonify({"error": "Username or email address is already registered."}), 400


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Please provide both username/email and password."}), 400

    user = login_user(username, password)
    if user:
        return jsonify(user)
    return jsonify({"error": "Invalid username or password."}), 401


# 4. Landlord Property Management
@app.route("/api/landlord/properties", methods=["POST"])
def add_landlord_property():
    data = request.json or {}
    house_id = data.get("house_id", f"TAM-{int(Path().stat().st_mtime)}")
    neighborhood = data.get("neighborhood")
    house_type = data.get("house_type", "2 Bedroom")
    monthly_rent_ghs = float(data.get("monthly_rent_ghs", 1000))
    rooms = int(data.get("rooms", 2))
    bathrooms = int(data.get("bathrooms", 1))

    conn = get_connection()
    conn.execute("""
        INSERT INTO properties (
            house_id, neighborhood, house_type, rooms, bathrooms,
            monthly_rent_ghs, water, electricity, compound, furnishing
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        house_id, neighborhood, house_type, rooms, bathrooms,
        monthly_rent_ghs, data.get("water", "Available"),
        data.get("electricity", "Prepaid"), data.get("compound", "Yes"),
        data.get("furnishing", "Unfurnished")
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Property listed successfully", "house_id": house_id})


@app.route("/api/landlord/properties/<house_id>", methods=["DELETE"])
def delete_landlord_property(house_id):
    conn = get_connection()
    conn.execute("DELETE FROM properties WHERE house_id = ?", (house_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Listing {house_id} removed successfully"})


# 5. Direct Enquiry API
@app.route("/api/enquiries", methods=["POST"])
def post_enquiry():
    data = request.json or {}
    conn = get_connection()
    conn.execute("""
        INSERT INTO enquiries (property_id, tenant_name, tenant_email, message)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("property_id"), data.get("tenant_name"),
        data.get("tenant_email"), data.get("message")
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Enquiry submitted successfully"})


if __name__ == "__main__":
    print("Serving Tamale House Market on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
