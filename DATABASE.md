# PostgreSQL setup

The Flask app uses PostgreSQL through `DATABASE_URL`. The app now loads `.env` automatically from the project root. To start a local database with Docker Desktop:

1. Copy `.env.example` to `.env`.
2. Run `docker compose up -d db` from the project directory.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Start the app with `python server.py` and open `http://localhost:5000`.

The schema is created and the rental CSV is seeded when the server starts. `src/house_search.py` no longer imports Streamlit in the Flask backend, which keeps the web server's runtime dependencies smaller.

For another PostgreSQL server, set `DATABASE_URL` in `.env` to its connection string. A local connection string is:

```text
postgresql://postgres:your-password@localhost:5432/tamale_house_market
```

Do not commit `.env` or put production credentials in source control. For authentication integration tests, set `TEST_DATABASE_URL` to a separate disposable PostgreSQL database; tests never use `DATABASE_URL` unless explicitly given that test URL.

The former SQLite file is not modified or automatically copied. Existing accounts, favourites, enquiries, and landlord listings in that file need an explicit data migration before switching a deployment to PostgreSQL. Seed properties are loaded from `data/tamale_house_rentals.csv` on first startup.
