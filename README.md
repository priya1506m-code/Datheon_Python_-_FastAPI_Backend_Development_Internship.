# FastAPI JWT + Async SQLAlchemy Notes API

Persistent REST API using FastAPI, SQLAlchemy 2.x async sessions, SQLite,
bcrypt password hashing, JWT bearer authentication, and a one-to-many
User -> Notes relationship.

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
```

Activate:
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install and configure:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` (Windows: `Copy-Item .env.example .env`;
macOS/Linux: `cp .env.example .env`). Set `SECRET_KEY` to a strong random
secret. Generate one using:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run:

```bash
uvicorn main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

SQLite tables are created at startup. The `app.db` file persists between
server restarts; do not delete it if you want to retain data.

## Routes

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/register` | No | Register user |
| POST | `/login` | No | Get JWT (form fields) |
| GET | `/users/me` | Yes | Current profile |
| POST | `/notes` | Yes | Create note |
| GET | `/notes` | Yes | List own notes |
| GET | `/notes/{note_id}` | Yes | Read own note |
| PUT | `/notes/{note_id}` | Yes | Update own note |
| DELETE | `/notes/{note_id}` | Yes | Delete own note |
| GET | `/dashboard` | Yes | User dashboard and note count |

## Quick test

1. POST `/register` with JSON:
   `{"username":"john","password":"mypassword123"}`
2. POST `/login` with form fields `username` and `password`; copy `access_token`.
3. Click **Authorize** in Swagger UI and authenticate.
4. POST `/notes` with JSON:
   `{"title":"My first note","content":"Saved in SQLite."}`
5. GET `/notes`; stop and restart the server, log in again, and GET `/notes`.
   Your note should remain.

## Data model and implementation

- `database.py`: async engine, `async_sessionmaker`, Base, and `get_db`.
- `models.py`: SQLAlchemy User and Note models with a one-to-many relationship.
- `schemas.py`: Pydantic request/response DTOs.
- `security.py`: bcrypt, JWT and `get_current_user`.
- `main.py`: API routes and startup table creation.
- Each note is scoped to its authenticated owner; users cannot access other
  users' notes through these endpoints.

## PostgreSQL

Install the async driver:

```bash
pip install asyncpg
```

Create a PostgreSQL database, then set in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/notes_db
```

## Production notes

This starter uses `Base.metadata.create_all()` for local convenience. Use
Alembic migrations for schema changes in production. Add tests, rate limiting,
HTTPS, secret management, backups, and monitoring before deployment.
