# Tamale House Market 🏠

**Tamale House Market** is a full-stack house-rental platform designed to connect landlords and prospective tenants in Tamale, Ghana. It provides property seekers with a verified way to discover, filter, and inquire about residential rental properties while giving house owners and landlords tools to showcase and manage their listings.

---

## 🎯 The Problem

Finding rental accommodation across Tamale is frequently time-consuming and fragmented. Prospective tenants face challenges discovering verified properties, comparing rental prices in Ghana Cedis (GH₵), and directly contacting landlords. Meanwhile, landlords often lack a centralized digital avenue to reach tenants and manage inquiries efficiently.

---

## 💡 The Solution

Tamale House Market addresses these issues with a secure, centralized web application where:

* **Tenants** can search and filter rental listings by suburb/neighbourhood, rental budget, room counts, bathrooms, and water availability.
* **Property Seekers** can save favourites, review detailed house specifications, and directly connect with landlords via WhatsApp or direct phone calls.
* **Landlords** have dedicated portal dashboards to list properties, edit rental details, toggle active/inactive availability, and manage tenant inquiries.
* **Secure Authentication & RBAC** ensures that sensitive property actions (creating, updating, deleting) are strictly restricted to verified listing owners.

---

## ✨ Features

### Public & Tenant Experience
* **Live Property Discovery**: Real-time browsing and filtering powered by PostgreSQL with fallback capability.
* **Multi-Criteria Filtering**: Filter by Tamale neighbourhood (*Nyohini*, *Lamashegu*, *Dungu*, *Vittin*, *Tishegu*, *Fuo*, *Kanvilli*, *Education Ridge*, etc.), min/max rent (GH₵), room count, and bathroom count.
* **Property Detail Pages**: Comprehensive house specifications, utility details (Prepaid/Postpaid electricity, pipe/tanker water, walled compounds), and photo previews.
* **Direct Communication**: One-click WhatsApp link and direct phone dialer formatted for Ghana phone numbers.
* **Tenant Dashboard**: Bookmark favourite listings and review sent direct rental enquiries.

### Landlord Portal
* **Listing Management**: Add new properties with custom rent, room specs, utilities, and photo previews.
* **Edit & Update**: In-place modal editing to adjust prices, specifications, and listing titles.
* **Availability Toggling**: Switch listings between active and inactive/occupied without deleting records.
* **Inquiries Inbox**: Review incoming inquiries from prospective tenants including contact information and messages.
* **IDOR Protection**: Backend guarantees landlords can only modify and delete their own properties.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.13, Flask 3.1
* **Database**: PostgreSQL 16
* **Database Driver**: Psycopg 3.3 (`psycopg[binary]`)
* **Password Hashing**: PBKDF2-HMAC-SHA256 (600,000 rounds with cryptographically secure random salts)
* **Session Management**: Secure cookie-based Flask sessions (`HttpOnly`, `SameSite=Lax`, `Secure` in production)
* **Frontend**: HTML5, Vanilla JavaScript, Responsive CSS3
* **Production WSGI**: Gunicorn / Waitress
* **Automated Testing**: Pytest 8.3

---

## 📁 Project Structure

```text
tamale_house_finder/
├── data/
│   ├── tamale_house_rentals.csv   # Initial property dataset seeded on startup
│   └── house_data.py              # Data exploration helper
├── frontend/                      # Static assets and views
│   ├── css/
│   │   ├── styles.css             # Core theme, variables & typography
│   │   ├── dashboard.css          # Landlord & tenant dashboard layouts
│   │   └── responsive.css         # Breakpoint rules for mobile & tablet
│   ├── js/
│   │   ├── main.js                # Core utility, auth sync & favourites
│   │   ├── auth.js                # Login & registration form handlers
│   │   ├── houses.js              # Property search & card rendering
│   │   ├── property.js            # Property details & enquiry submission
│   │   ├── landlord.js            # Landlord portal CRUD & modal editor
│   │   └── tenant.js              # Tenant dashboard, saved houses & inquiries
│   ├── landlord/                  # Landlord dashboard pages
│   ├── tenant/                    # Tenant dashboard pages
│   ├── index.html                 # Homepage with hero search & featured listings
│   ├── houses.html                # Browse & search listings page
│   ├── property.html              # Individual listing details page
│   ├── login.html                 # User authentication login
│   ├── register.html              # Role-based user registration
│   ├── about.html                 # Platform standards & mission
│   └── contact.html               # Platform support contact page
├── src/
│   ├── auth.py                    # Password hashing, verification & user queries
│   ├── database.py                # PostgreSQL schema, migrations, and query builders
│   └── house_search.py            # Pandas-based search logic fallback
├── test/
│   ├── test_api_endpoints.py      # Integration tests for auth sessions, landlord CRUD, favourites & enquiries
│   ├── test_auth.py               # Unit & integration tests for password hashing & registration
│   └── test_house_logic.py        # Logic tests for rental budget & house filtering
├── .env.example                   # Example environment configuration template
├── .gitignore                     # Git exclusion rules
├── DATABASE.md                    # Database documentation
├── docker-compose.yml             # Local PostgreSQL service container
├── requirements.txt               # Python package dependencies
├── server.py                      # Flask REST API entry point
└── wsgi.py                        # Production WSGI application wrapper
```

---

## ⚙️ Getting Started

### Prerequisites

* Python 3.10+
* PostgreSQL 14+ (or Docker Desktop)
* Git

### 1. Clone & Navigate

```bash
git clone https://github.com/Ninkila/tamale_house_project.git
cd tamale_house_finder
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` to configure your PostgreSQL credentials:

```ini
FLASK_ENV=development
SECRET_KEY=replace-with-a-random-secret-key
DATABASE_URL=postgresql://tamale_user:tamale_dev_password@localhost:5432/tamale_house_market
TEST_DATABASE_URL=postgresql://tamale_user:tamale_dev_password@localhost:5432/tamale_house_market_test
```

### 5. Start PostgreSQL

Using Docker Compose:

```bash
docker compose up -d db
```

Or connect to an existing local/remote PostgreSQL instance with the configured `DATABASE_URL`.

### 6. Run the Application

```bash
python server.py
```

Open [http://localhost:5000](http://localhost:5000) in your web browser. The database schema and seed data are automatically initialized on startup.

---

## 🧪 Running Automated Tests

Run the complete test suite with:

```bash
pytest -v
```

Tests run against the isolated test database configured in `TEST_DATABASE_URL` so that existing development or production data is never modified or reset.

---

## 🚀 Deployment Guide (Render)

### Deploying to Render

This project includes a production blueprint specification (`render.yaml`) for one-click deployment on [Render](https://render.com).

1. **Connect Repository**: Link your GitHub repository (`Ninkila/tamale_house_project`) to your Render account.
2. **New Blueprint**: Go to **Blueprints** on Render and select this repository.
3. **Automatic Provisioning**: Render will automatically:
   * Create a managed PostgreSQL database (`tamale_house_market`).
   * Provision the Python Web Service with `pip install -r requirements.txt`.
   * Configure the startup command: `gunicorn wsgi:app`.
   * Automatically generate a secure, high-entropy `SECRET_KEY`.
   * Wire `DATABASE_URL` from the provisioned database.
4. **Health Check**: Set health check path to `/health`.

### Environment Variables for Production

| Variable | Description | Requirement | Example |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Application environment mode | Optional (`production` default) | `production` |
| `SECRET_KEY` | High-entropy secret for signing session cookies | **Required** (Refuses boot if missing in production) | Generated random 32+ char string |
| `DATABASE_URL` | PostgreSQL connection string | **Required** | `postgresql://user:pass@host:5432/dbname` |
| `PORT` | Listening port (Render provides automatically) | Optional (defaults to 5000) | `10000` |
| `SESSION_COOKIE_SECURE` | Enforces HTTPS-only cookies | Optional (defaults to `true` in production) | `true` |

> [!IMPORTANT]
> **Secret Key Invalidation Note**: Updating or rotating `SECRET_KEY` invalidates any existing cookie sessions signed with the previous key. Users will simply be prompted to log in again upon their next visit.

### Health Check Endpoint

* `GET /health`
  * Returns `200 OK` with `{"status": "ok", "database": "ready"}` when the app and PostgreSQL connection are live.
  * Returns `503 Service Unavailable` with `{"status": "degraded", "database": "unavailable"}` if PostgreSQL is unreachable.

### Running with a Production WSGI Server Locally

On Linux / macOS:

```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

On Windows:

```bash
waitress-serve --port=5000 wsgi:app
```

---

## 🔒 Security Practices

* **Server-Side Validation**: All registration, property listing, and enquiry requests validate fields on the backend.
* **Parameterized Queries**: Every SQL query uses `%s` psycopg parameterization to guard against SQL injection.
* **Session Security**: Cookies are flagged `HttpOnly`, `SameSite=Lax`, and `Secure` in production.
* **Role-Based Access Control**: Sensitive landlord actions require authenticated landlord sessions; tenants cannot perform landlord actions.
* **Repository Hygiene**: Sensitive `.env` files, virtual environments, local SQLite caches, and test artifacts are strictly excluded by `.gitignore`.

---

## 📄 License

Tamale House Market is released under the MIT License.
