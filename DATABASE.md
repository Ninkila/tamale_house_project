# PostgreSQL setup

The Flask app uses PostgreSQL through `DATABASE_URL`. The app loads `.env` automatically from the project root. To start a local database with Docker Desktop:

1. Copy `.env.example` to `.env`.
2. Run `docker compose up -d db` from the project directory.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Start the app with `python server.py` and open `http://localhost:5000`.

The schema is created and initial seed records from `data/tamale_house_rentals.csv` are seeded safely and idempotently on startup. Existing rows and columns are never overwritten or duplicated.

For another PostgreSQL server, set `DATABASE_URL` in `.env` to its connection string. A local connection string is:

```text
postgresql://postgres:your-password@localhost:5432/tamale_house_market
```

Do not commit `.env` or put production credentials in source control. For authentication integration tests, set `TEST_DATABASE_URL` to a separate disposable PostgreSQL database; tests never use `DATABASE_URL` unless explicitly given that test URL.

### Migration & Data Safety

* Tables (`users`, `properties`, `favourites`, `enquiries`) and indexes are created idempotently with `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.
* Schema updates add columns with `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...` so existing records are preserved without table recreation or truncation.
* Seeding only executes if the `properties` table is empty (`SELECT EXISTS (SELECT 1 FROM properties)`).

### Backup and Restore

To take a logical backup before maintenance or deployment:

```bash
pg_dump -U tamale_user -d tamale_house_market -F c -b -v -f tamale_backup.dump
```

To restore from a backup:

```bash
pg_restore -U tamale_user -d tamale_house_market -v tamale_backup.dump
```

### Health Check

The application exposes `GET /health` which actively executes `SELECT 1` against PostgreSQL to confirm live database connectivity. If the database connection fails, it returns HTTP 503 without leaking internal credentials.

### Administrator analytics

Set `ADMIN_EMAILS` in `.env` to one or more comma-separated addresses. An account registered with a listed address is assigned the administrator role by the server. Open `/admin/dashboard.html` after signing in to view protected traffic, listing, enquiry, and account metrics. The public registration form never offers an administrator role.
