import os
import re
from contextlib import closing
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
import psycopg
from src.database import create_users_table, get_connection
from src.auth import register_user, login_user
from src.house_search import find_houses

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV", "production").lower() == "production"

# Keep the web app available when PostgreSQL has not been configured yet.
DATABASE_READY = False
try:
    create_users_table()
    DATABASE_READY = True
except (psycopg.Error, RuntimeError) as exc:
    app.logger.warning("PostgreSQL is not ready; database-backed routes will return 503: %s", exc)


@app.before_request
def ensure_auth_database():
    global DATABASE_READY
    if not request.path.startswith("/api/auth/") or DATABASE_READY:
        return None
    try:
        create_users_table()
        DATABASE_READY = True
    except (psycopg.Error, RuntimeError) as exc:
        app.logger.error("PostgreSQL is unavailable for authentication: %s", exc)
        return jsonify({
            "error": "PostgreSQL is unavailable. Set DATABASE_URL in the project .env file and start the database."
        }), 503
    return None


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
        with closing(conn), conn:
            rows = conn.execute("SELECT * FROM properties").fetchall()
        return jsonify(rows)


# 2. Get Single Property Details
@app.route("/api/houses/<house_id>", methods=["GET"])
def get_house_detail(house_id):
    conn = get_connection()
    with closing(conn), conn:
        row = conn.execute("SELECT * FROM properties WHERE house_id = %s", (house_id,)).fetchone()

    if row:
        return jsonify(row)
    return jsonify({"error": "Property not found"}), 404


# 3. User Authentication
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Registration details must be a JSON object."}), 400
    if any(not isinstance(data.get(field, ""), str) for field in ("username", "email", "password", "role", "full_name")):
        return jsonify({"error": "Registration fields must be strings."}), 400
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password", "")
    role = (data.get("role") or "").strip().lower()
    full_name = (data.get("full_name") or "").strip()

    if not username or not email or not password or not role:
        return jsonify({"error": "Missing required fields. Please specify your account role (Landlord or Tenant)."}), 400

    if role not in ["landlord", "tenant"]:
        return jsonify({"error": "Invalid role specified. Role must be 'landlord' or 'tenant'."}), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    try:
        success = register_user(username, email, password, role=role, full_name=full_name)
    except psycopg.Error as exc:
        app.logger.exception("PostgreSQL registration failed: %s", exc)
        return jsonify({"error": "PostgreSQL could not save the account. Check the database connection and try again."}), 503
    if success:
        return jsonify({
            "message": "User registered successfully",
            "username": username,
            "email": email.lower(),
            "role": role,
            "full_name": full_name or username
        })
    return jsonify({"error": "Username or email address is already registered."}), 400


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Login details must be a JSON object."}), 400
    if any(not isinstance(data.get(field, ""), str) for field in ("username", "password")):
        return jsonify({"error": "Login fields must be strings."}), 400
    username = (data.get("username") or "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Please provide both username/email and password."}), 400

    try:
        user = login_user(username, password)
    except psycopg.Error as exc:
        app.logger.exception("PostgreSQL login failed: %s", exc)
        return jsonify({"error": "PostgreSQL is unavailable. Check the database connection and try again."}), 503
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
    with closing(conn), conn:
        conn.execute("""
        INSERT INTO properties (
            house_id, neighborhood, house_type, rooms, bathrooms,
            monthly_rent_ghs, water, electricity, compound, furnishing
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        house_id, neighborhood, house_type, rooms, bathrooms,
        monthly_rent_ghs, data.get("water", "Available"),
        data.get("electricity", "Prepaid"), data.get("compound", "Yes"),
        data.get("furnishing", "Unfurnished")
    ))

    return jsonify({"message": "Property listed successfully", "house_id": house_id})


@app.route("/api/landlord/properties/<house_id>", methods=["DELETE"])
def delete_landlord_property(house_id):
    conn = get_connection()
    with closing(conn), conn:
        conn.execute("DELETE FROM properties WHERE house_id = %s", (house_id,))
    return jsonify({"message": f"Listing {house_id} removed successfully"})


# 5. Direct Enquiry API
@app.route("/api/enquiries", methods=["POST"])
def post_enquiry():
    data = request.json or {}
    conn = get_connection()
    with conn:
        conn.execute("""
        INSERT INTO enquiries (property_id, tenant_name, tenant_email, message)
        VALUES (%s, %s, %s, %s)
    """, (
        data.get("property_id"), data.get("tenant_name"),
        data.get("tenant_email"), data.get("message")
    ))
    return jsonify({"message": "Enquiry submitted successfully"})


@app.route("/health")
def health_check():
    if DATABASE_READY:
        return jsonify({"status": "ok", "database": "ready"})
    return jsonify({"status": "degraded", "database": "unavailable"}), 503


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"Serving Tamale House Market on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
