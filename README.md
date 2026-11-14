# Book Management API

A beginner-friendly REST API built with FastAPI, Pydantic, and Uvicorn.

## Requirements
- Python 3.10+
- pip

## Setup

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn main:app --reload
```

Open:
- API root: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/books` | Create a book |
| GET | `/books` | List and filter books |
| GET | `/books/{book_id}` | Retrieve one book |
| PUT | `/books/{book_id}` | Update a book |
| DELETE | `/books/{book_id}` | Delete a book |

## Example POST body

```json
{
  "title": "The Alchemist",
  "author": "Paulo Coelho",
  "publication_year": 1988,
  "genre": "Fiction"
}
```

## Filtering examples

- `/books?author=paulo`
- `/books?title=alchemist`
- `/books?publication_year=1988`
- Combine filters: `/books?author=paulo&publication_year=1988`

## Notes
- Book IDs are generated automatically.
- The API uses in-memory storage for simplicity. All records are cleared when the server stops.
- `PUT` updates only the fields supplied in the request; omitted fields remain unchanged.
- Invalid request data is automatically rejected by Pydantic with HTTP 422.
