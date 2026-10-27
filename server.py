import os
import re
from contextlib import closing
from functools import wraps
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, session
import psycopg
from dotenv import load_dotenv

# Load environment configuration from .env if present
load_dotenv()

from src.database import (
    create_users_table,
    get_connection,
    get_property_by_id,
    query_properties,
    format_property_dict,
)
from src.auth import (
    register_user,
    login_user,
    get_user_by_id,
    update_user_profile,
)
from src.house_search import find_houses

app = Flask(__name__, static_folder="frontend", static_url_path="")

# --- APPLICATION SECURITY & SECRET-KEY CONFIGURATION ---

DEV_FALLBACK_SECRET = "tamale-insecure-dev-only-secret-key-do-not-use-in-production"
INSECURE_SECRETS = {
    "mimi121269reed",
    "replace-with-a-secure-random-secret-key-in-production",
    DEV_FALLBACK_SECRET,
}


def init_security_config(flask_app):
    """
    Configure secret key and session cookies safely based on runtime environment.
    Enforces that production environments MUST supply an independent, strong SECRET_KEY.
    """
    raw_env = (
        os.environ.get("FLASK_ENV")
        or os.environ.get("ENVIRONMENT")
        or "production"
    ).strip().lower()
    is_prod = raw_env not in {"development", "dev", "test", "testing"}
    secret = os.environ.get("SECRET_KEY")

    if is_prod:
        if not secret or secret.strip() in INSECURE_SECRETS or len(secret.strip()) < 16:
            raise RuntimeError(
                "FATAL: Production requires a strong SECRET_KEY environment variable (minimum 16 characters). "
                "Please configure SECRET_KEY in your production hosting environment."
            )
        flask_app.config["SECRET_KEY"] = secret.strip()
    else:
        if not secret or secret.strip() in INSECURE_SECRETS:
            flask_app.logger.warning(
                "Running in non-production mode with development fallback SECRET_KEY. "
                "Set a strong SECRET_KEY before deploying to production."
            )
            flask_app.config["SECRET_KEY"] = DEV_FALLBACK_SECRET
        else:
            flask_app.config["SECRET_KEY"] = secret.strip()

    # Session cookie hardening
    flask_app.config["SESSION_COOKIE_HTTPONLY"] = True
    flask_app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if is_prod:
        # Default Secure=True for production HTTPS cookies
        secure_cookie_env = os.environ.get("SESSION_COOKIE_SECURE", "true").strip().lower()
        flask_app.config["SESSION_COOKIE_SECURE"] = secure_cookie_env not in {"false", "0", "no"}
    else:
        secure_cookie_env = os.environ.get("SESSION_COOKIE_SECURE", "false").strip().lower()
        flask_app.config["SESSION_COOKIE_SECURE"] = secure_cookie_env in {"true", "1", "yes"}

    return is_prod


IS_PRODUCTION = init_security_config(app)

DATABASE_READY = False
try:
    create_users_table()
    DATABASE_READY = True
except (psycopg.Error, RuntimeError) as exc:
    app.logger.warning("PostgreSQL is not ready; database-backed routes will return 503: %s", exc)


@app.before_request
def ensure_auth_database():
    global DATABASE_READY
    if not request.path.startswith("/api/") or DATABASE_READY:
        return None
    try:
        create_users_table()
        DATABASE_READY = True
    except (psycopg.Error, RuntimeError) as exc:
        app.logger.error("PostgreSQL is unavailable: %s", exc)
        return jsonify({
            "error": "PostgreSQL is unavailable. Set DATABASE_URL in the project .env file and start the database."
        }), 503
    return None


# --- AUTHORIZATION DECORATORS ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required. Please log in to proceed."}), 401
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                return jsonify({"error": "Authentication required. Please log in to proceed."}), 401
            current_role = session.get("role")
            if current_role != required_role:
                return jsonify({
                    "error": f"Access forbidden. This action requires a {required_role} account."
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# --- SERVE FRONTEND STATIC FILES ---

@app.route("/")
def serve_index():
    return send_from_directory("frontend", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    target = Path("frontend") / path
    if target.exists() and not target.is_dir():
        return send_from_directory("frontend", path)
    return send_from_directory("frontend", "index.html")


# --- REST API ENDPOINTS ---

# 1. Browse & Search Houses (PostgreSQL backed with CSV fallback)
@app.route("/api/houses", methods=["GET"])
def get_houses():
    budget = request.args.get("budget", request.args.get("maxRent"))
    min_rent = request.args.get("minRent", request.args.get("min_rent"))
    location = request.args.get("neighborhood", request.args.get("location", ""))
    rooms = request.args.get("rooms", request.args.get("bedroom"))
    bathrooms = request.args.get("bathrooms", request.args.get("bathroom"))
    water = request.args.get("water", "Any")
    house_type = request.args.get("houseType", request.args.get("house_type"))
    available_only = request.args.get("available_only", "false").lower() in {"true", "1", "yes"}

    try:
        budget_val = float(budget) if budget is not None and budget != "" else None
        min_rent_val = float(min_rent) if min_rent is not None and min_rent != "" else None
        rooms_val = int(rooms) if rooms is not None and rooms != "" else None
        bathrooms_val = int(bathrooms) if bathrooms is not None and bathrooms != "" else None
    except ValueError:
        return jsonify({"error": "Invalid filter numeric parameter provided."}), 400

    conn = None
    try:
        conn = get_connection()
        with closing(conn), conn:
            houses = query_properties(
                conn,
                budget=budget_val,
                min_rent=min_rent_val,
                neighborhood=location,
                rooms=rooms_val,
                bathrooms=bathrooms_val,
                water=water,
                house_type=house_type,
                available_only=available_only,
            )
            return jsonify(houses)
    except (psycopg.Error, RuntimeError) as exc:
        app.logger.error("PostgreSQL property query failed: %s", exc)
        return jsonify({
            "error": "Property database is temporarily unavailable. Please try again shortly."
        }), 503
    except Exception as exc:
        app.logger.exception("Unexpected error while searching properties: %s", exc)
        return jsonify({"error": "Failed to retrieve properties."}), 500


# 2. Get Single Property Details
@app.route("/api/houses/<house_id>", methods=["GET"])
def get_house_detail(house_id):
    try:
        conn = get_connection()
        with closing(conn), conn:
            property_detail = get_property_by_id(conn, house_id)
        if property_detail:
            return jsonify(property_detail)
        return jsonify({"error": "Property not found"}), 404
    except Exception as exc:
        app.logger.exception("Failed to retrieve house %s: %s", house_id, exc)
        return jsonify({"error": "Failed to retrieve property details."}), 500


# 3. User Authentication & Profile
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
    phone = (data.get("phone") or "0241234567").strip()

    if not username or not email or not password or not role:
        return jsonify({"error": "Missing required fields. Please specify your account role (Landlord or Tenant)."}), 400

    if role not in ["landlord", "tenant"]:
        return jsonify({"error": "Invalid role specified. Role must be 'landlord' or 'tenant'."}), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    try:
        success = register_user(username, email, password, role=role, full_name=full_name, phone=phone)
    except psycopg.Error as exc:
        app.logger.exception("PostgreSQL registration failed: %s", exc)
        return jsonify({"error": "PostgreSQL could not save the account. Check the database connection and try again."}), 503

    if success:
        user = login_user(username, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["email"] = user["email"]
            session["full_name"] = user["full_name"]
            return jsonify({
                "message": "User registered successfully",
                "user": user,
            }), 201

        return jsonify({
            "message": "User registered successfully",
            "username": username,
            "email": email.lower(),
            "role": role,
            "full_name": full_name or username,
        }), 201

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
        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["email"] = user["email"]
        session["full_name"] = user["full_name"]
        return jsonify(user)

    return jsonify({"error": "Invalid username or password."}), 401


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@app.route("/api/auth/me", methods=["GET"])
def api_get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False, "user": None}), 200

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({"authenticated": False, "user": None}), 200

    return jsonify({"authenticated": True, "user": user}), 200


@app.route("/api/auth/profile", methods=["PUT"])
@login_required
def api_update_profile():
    data = request.get_json(silent=True) or {}
    user_id = session["user_id"]

    updated = update_user_profile(
        user_id,
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        show_whatsapp=data.get("show_whatsapp"),
        show_phone=data.get("show_phone"),
    )
    if updated:
        session["full_name"] = updated["full_name"]
        return jsonify({"message": "Profile updated successfully", "user": updated})
    return jsonify({"error": "Failed to update profile."}), 400


# 4. Landlord Property Management
@app.route("/api/landlord/properties", methods=["GET"])
@role_required("landlord")
def get_landlord_properties():
    landlord_id = session["user_id"]
    conn = get_connection()
    with closing(conn), conn:
        props = query_properties(conn, landlord_id=landlord_id, available_only=False)
    return jsonify(props)


@app.route("/api/landlord/properties", methods=["POST"])
@role_required("landlord")
def add_landlord_property():
    data = request.get_json(silent=True) or {}
    landlord_id = session["user_id"]

    neighborhood = (data.get("neighborhood") or "").strip()
    house_type = (data.get("house_type") or "2 Bedroom").strip()
    title = (data.get("title") or f"{house_type} in {neighborhood}").strip()
    description = (data.get("description") or "").strip()
    image = (data.get("image") or "").strip()

    try:
        rent = float(data.get("monthly_rent_ghs") or data.get("rent", 0))
        rooms = int(data.get("rooms", 2))
        bathrooms = int(data.get("bathrooms", 1))
    except (ValueError, TypeError):
        return jsonify({"error": "Rent, rooms, and bathrooms must be valid numeric values."}), 400

    if not neighborhood:
        return jsonify({"error": "Neighbourhood is required."}), 400
    if rent <= 0:
        return jsonify({"error": "Monthly rent must be greater than 0 GH₵."}), 400
    if rooms < 1 or bathrooms < 0:
        return jsonify({"error": "Please provide valid room and bathroom counts."}), 400

    conn = get_connection()
    with closing(conn), conn:
        # Generate next house identifier
        max_row = conn.execute("SELECT house_id FROM properties WHERE house_id LIKE 'TAM-%'").fetchall()
        max_id_num = 0
        for r in max_row:
            digits = "".join(c for c in r["house_id"] if c.isdigit())
            if digits:
                max_id_num = max(max_id_num, int(digits))
        house_id = f"TAM-{max_id_num + 1:03d}"

        # Get landlord contact info
        user = get_user_by_id(landlord_id)
        phone = data.get("landlord_phone") or (user.get("phone") if user else "0241234567")

        conn.execute("""
            INSERT INTO properties (
                house_id, neighborhood, house_type, rooms, bathrooms,
                monthly_rent_ghs, water, electricity, compound, furnishing,
                landlord_id, landlord_phone, show_whatsapp, show_phone,
                available, image, title, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            house_id, neighborhood, house_type, rooms, bathrooms,
            rent, data.get("water", "Available"),
            data.get("electricity", "Prepaid"), data.get("compound", "Yes"),
            data.get("furnishing", "Unfurnished"),
            landlord_id, phone,
            bool(data.get("show_whatsapp", True)),
            bool(data.get("show_phone", True)),
            True, image, title, description,
        ))

        created = get_property_by_id(conn, house_id)

    return jsonify({"message": "Property listed successfully", "property": created, "house_id": house_id}), 201


@app.route("/api/landlord/properties/<house_id>", methods=["PUT"])
@role_required("landlord")
def update_landlord_property(house_id):
    data = request.get_json(silent=True) or {}
    landlord_id = session["user_id"]

    conn = get_connection()
    with closing(conn), conn:
        existing = conn.execute(
            "SELECT landlord_id FROM properties WHERE house_id = %s", (house_id,)
        ).fetchone()

        if not existing:
            return jsonify({"error": "Property not found."}), 404
        if existing["landlord_id"] != landlord_id:
            return jsonify({"error": "Forbidden: You do not own this listing."}), 403

        try:
            rent = float(data.get("monthly_rent_ghs")) if data.get("monthly_rent_ghs") is not None else None
            rooms = int(data.get("rooms")) if data.get("rooms") is not None else None
            bathrooms = int(data.get("bathrooms")) if data.get("bathrooms") is not None else None
        except (ValueError, TypeError):
            return jsonify({"error": "Rent, rooms, and bathrooms must be valid numeric values."}), 400

        updates = []
        params = []
        if data.get("neighborhood"):
            updates.append("neighborhood = %s")
            params.append(data["neighborhood"].strip())
        if data.get("house_type"):
            updates.append("house_type = %s")
            params.append(data["house_type"].strip())
        if rent is not None and rent > 0:
            updates.append("monthly_rent_ghs = %s")
            params.append(rent)
        if rooms is not None and rooms >= 1:
            updates.append("rooms = %s")
            params.append(rooms)
        if bathrooms is not None and bathrooms >= 0:
            updates.append("bathrooms = %s")
            params.append(bathrooms)
        if "water" in data:
            updates.append("water = %s")
            params.append(data["water"])
        if "electricity" in data:
            updates.append("electricity = %s")
            params.append(data["electricity"])
        if "compound" in data:
            updates.append("compound = %s")
            params.append(data["compound"])
        if "furnishing" in data:
            updates.append("furnishing = %s")
            params.append(data["furnishing"])
        if "image" in data:
            updates.append("image = %s")
            params.append(data["image"])
        if "title" in data:
            updates.append("title = %s")
            params.append(data["title"])
        if "description" in data:
            updates.append("description = %s")
            params.append(data["description"])
        if "available" in data:
            updates.append("available = %s")
            params.append(bool(data["available"]))

        if updates:
            params.append(house_id)
            conn.execute(f"UPDATE properties SET {', '.join(updates)} WHERE house_id = %s", params)

        updated_property = get_property_by_id(conn, house_id)

    return jsonify({"message": "Property updated successfully", "property": updated_property})


@app.route("/api/landlord/properties/<house_id>/status", methods=["PATCH"])
@role_required("landlord")
def toggle_landlord_property_status(house_id):
    data = request.get_json(silent=True) or {}
    landlord_id = session["user_id"]

    conn = get_connection()
    with closing(conn), conn:
        existing = conn.execute(
            "SELECT landlord_id, available FROM properties WHERE house_id = %s", (house_id,)
        ).fetchone()

        if not existing:
            return jsonify({"error": "Property not found."}), 404
        if existing["landlord_id"] != landlord_id:
            return jsonify({"error": "Forbidden: You do not own this listing."}), 403

        new_status = data.get("available")
        if new_status is None:
            new_status = not existing["available"]
        else:
            new_status = bool(new_status)

        conn.execute("UPDATE properties SET available = %s WHERE house_id = %s", (new_status, house_id))

    return jsonify({"message": "Status updated successfully", "house_id": house_id, "available": new_status})


@app.route("/api/landlord/properties/<house_id>", methods=["DELETE"])
@role_required("landlord")
def delete_landlord_property(house_id):
    landlord_id = session["user_id"]

    conn = get_connection()
    with closing(conn), conn:
        existing = conn.execute(
            "SELECT landlord_id FROM properties WHERE house_id = %s", (house_id,)
        ).fetchone()

        if not existing:
            return jsonify({"error": "Property not found."}), 404
        if existing["landlord_id"] != landlord_id:
            return jsonify({"error": "Forbidden: You do not own this listing."}), 403

        conn.execute("DELETE FROM favourites WHERE house_id = %s", (house_id,))
        conn.execute("DELETE FROM enquiries WHERE property_id = %s", (house_id,))
        conn.execute("DELETE FROM properties WHERE house_id = %s", (house_id,))

    return jsonify({"message": f"Listing {house_id} removed successfully"})


# 5. Enquiries Management
@app.route("/api/enquiries", methods=["POST"])
def post_enquiry():
    data = request.get_json(silent=True) or {}
    property_id = data.get("property_id")
    message = (data.get("message") or "").strip()

    if not property_id or not message:
        return jsonify({"error": "Property ID and inquiry message are required."}), 400

    tenant_id = session.get("user_id")
    tenant_name = (data.get("tenant_name") or session.get("full_name") or session.get("username") or "").strip()
    tenant_email = (data.get("tenant_email") or session.get("email") or "").strip()

    if not tenant_name or not tenant_email:
        return jsonify({"error": "Your name and contact email are required to submit an inquiry."}), 400

    conn = get_connection()
    with closing(conn), conn:
        prop = conn.execute("SELECT landlord_id FROM properties WHERE house_id = %s", (property_id,)).fetchone()
        if not prop:
            return jsonify({"error": f"Property '{property_id}' not found."}), 404
        landlord_id = prop["landlord_id"]

        conn.execute("""
            INSERT INTO enquiries (property_id, tenant_id, landlord_id, tenant_name, tenant_email, message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (property_id, tenant_id, landlord_id, tenant_name, tenant_email, message))

    return jsonify({"message": "Enquiry submitted successfully"}), 201


@app.route("/api/landlord/enquiries", methods=["GET"])
@role_required("landlord")
def get_landlord_enquiries():
    landlord_id = session["user_id"]
    conn = get_connection()
    with closing(conn), conn:
        rows = conn.execute("""
            SELECT
                e.id,
                e.property_id,
                p.house_type,
                p.neighborhood,
                COALESCE(p.title, p.house_type || ' in ' || p.neighborhood) AS house_title,
                e.tenant_name,
                e.tenant_email,
                e.message,
                e.status,
                e.created_at
            FROM enquiries e
            JOIN properties p ON e.property_id = p.house_id
            WHERE e.landlord_id = %s OR p.landlord_id = %s
            ORDER BY e.created_at DESC
        """, (landlord_id, landlord_id)).fetchall()

    enquiries = []
    for r in rows:
        d = dict(r)
        if "created_at" in d and hasattr(d["created_at"], "isoformat"):
            d["created_at"] = d["created_at"].isoformat()
        enquiries.append(d)

    return jsonify(enquiries)


@app.route("/api/tenant/enquiries", methods=["GET"])
@login_required
def get_tenant_enquiries():
    tenant_id = session["user_id"]
    conn = get_connection()
    with closing(conn), conn:
        rows = conn.execute("""
            SELECT
                e.id,
                e.property_id,
                p.house_type,
                p.neighborhood,
                COALESCE(p.title, p.house_type || ' in ' || p.neighborhood) AS house_title,
                e.tenant_name,
                e.tenant_email,
                e.message,
                e.status,
                e.created_at
            FROM enquiries e
            JOIN properties p ON e.property_id = p.house_id
            WHERE e.tenant_id = %s
            ORDER BY e.created_at DESC
        """, (tenant_id,)).fetchall()

    enquiries = []
    for r in rows:
        d = dict(r)
        if "created_at" in d and hasattr(d["created_at"], "isoformat"):
            d["created_at"] = d["created_at"].isoformat()
        enquiries.append(d)

    return jsonify(enquiries)


# 6. Favourites Management (Saved Properties)
@app.route("/api/favourites", methods=["GET"])
@login_required
def get_user_favourites():
    tenant_id = session["user_id"]
    conn = get_connection()
    with closing(conn), conn:
        rows = conn.execute("""
            SELECT p.*, u.username AS owner_username, u.full_name AS owner_name
            FROM favourites f
            JOIN properties p ON f.house_id = p.house_id
            LEFT JOIN users u ON p.landlord_id = u.id
            WHERE f.tenant_id = %s
            ORDER BY f.created_at DESC
        """, (tenant_id,)).fetchall()

    return jsonify([format_property_dict(r) for r in rows])


@app.route("/api/favourites/<house_id>", methods=["POST"])
@login_required
def add_favourite(house_id):
    tenant_id = session["user_id"]
    conn = get_connection()
    with closing(conn), conn:
        prop = conn.execute("SELECT 1 FROM properties WHERE house_id = %s", (house_id,)).fetchone()
        if not prop:
            return jsonify({"error": f"Property '{house_id}' not found."}), 404
        conn.execute("""
            INSERT INTO favourites (tenant_id, house_id)
            VALUES (%s, %s)
            ON CONFLICT (tenant_id, house_id) DO NOTHING
        """, (tenant_id, house_id))
    return jsonify({"message": f"Property {house_id} saved to favourites", "house_id": house_id, "saved": True})


@app.route("/api/favourites/<house_id>", methods=["DELETE"])
@login_required
def remove_favourite(house_id):
    tenant_id = session["user_id"]
    conn = get_connection()
    with closing(conn), conn:
        conn.execute("DELETE FROM favourites WHERE tenant_id = %s AND house_id = %s", (tenant_id, house_id))
    return jsonify({"message": f"Property {house_id} removed from favourites", "house_id": house_id, "saved": False})


@app.route("/health")
def health_check():
    global DATABASE_READY
    try:
        conn = get_connection()
        with closing(conn), conn:
            conn.execute("SELECT 1")
        DATABASE_READY = True
        return jsonify({"status": "ok", "database": "ready"}), 200
    except Exception as exc:
        app.logger.warning("Database health check ping failed: %s", exc)
        DATABASE_READY = False
        return jsonify({"status": "degraded", "database": "unavailable"}), 503


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"Serving Tamale House Market on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
