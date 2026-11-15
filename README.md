# FastAPI JWT Authentication

A small starter API demonstrating user registration, bcrypt password hashing,
OAuth2 password login, signed JWT access tokens, and protected routes.

## Requirements

- Python 3.10+
- pip

## Setup

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\\Scripts\\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

**macOS / Linux**
```bash
cp .env.example .env
```

**Windows PowerShell**
```powershell
Copy-Item .env.example .env
```

Replace `SECRET_KEY` in `.env` with a long, random secret. For example, generate
one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Run the API:

```bash
uvicorn main:app --reload
```

Open the interactive API documentation at http://127.0.0.1:8000/docs.
 Swagger UI: http://127.0.0.1:8000/docs

## Endpoints

| Method | Endpoint | Authentication |
|---|---|---|
| POST | `/register` | Not required |
| POST | `/login` | Not required |
| GET | `/users/me` | Bearer token required |
| GET | `/dashboard` | Bearer token required |

## Test in Swagger UI

1. Use `POST /register` with a JSON body:

   ```json
   {
     "username": "john",
     "password": "mypassword123"
   }
   ```

2. Use `POST /login`. This endpoint expects form fields (`username` and
   `password`), not a JSON body.
3. Copy the returned `access_token`.
4. Click **Authorize** in Swagger UI and enter the username/password, or use
   the token as a Bearer token in an API client.
5. Call `GET /users/me` or `GET /dashboard`.
6. Call a protected endpoint without a token to confirm it returns HTTP 401.

## Notes

- This project uses an in-memory dictionary for demonstration. Registered users
  disappear when the server restarts. Use a database such as PostgreSQL for
  persistent storage.
- Passwords are hashed with bcrypt; plaintext passwords are never stored.
- Passwords are limited to 72 characters because bcrypt has a 72-byte input
  limit. For production, validate UTF-8 byte length as well.
- Use HTTPS in production, protect your secret key, add login rate limiting,
  and design a refresh-token/revocation strategy if needed.
- This is a learning starter, not a complete production identity system.
