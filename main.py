from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="Book Management API",
    description="A simple REST API to create, read, update, delete, and filter books.",
    version="1.0.0",
)


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=120)
    publication_year: int = Field(..., ge=0, le=2100)
    genre: Optional[str] = Field(default=None, max_length=80)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=120)
    publication_year: Optional[int] = Field(default=None, ge=0, le=2100)
    genre: Optional[str] = Field(default=None, max_length=80)


class Book(BookCreate):
    id: int


# In-memory storage. Data resets whenever the server restarts.
books: dict[int, Book] = {}
next_book_id = 1


@app.get("/", tags=["General"])
def root():
    return {"message": "Welcome to the Book Management API", "docs": "/docs"}


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book_data: BookCreate):
    global next_book_id

    book = Book(id=next_book_id, **book_data.model_dump())
    books[next_book_id] = book
    next_book_id += 1
    return book


@app.get("/books", response_model=list[Book], tags=["Books"])
def get_books(
    title: Optional[str] = Query(default=None, description="Filter by title (case-insensitive partial match)"),
    author: Optional[str] = Query(default=None, description="Filter by author (case-insensitive partial match)"),
    publication_year: Optional[int] = Query(default=None, ge=0, le=2100),
):
    results = list(books.values())

    if title:
        results = [book for book in results if title.casefold() in book.title.casefold()]
    if author:
        results = [book for book in results if author.casefold() in book.author.casefold()]
    if publication_year is not None:
        results = [book for book in results if book.publication_year == publication_year]

    return results


@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int):
    book = books.get(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, book_data: BookUpdate):
    existing_book = books.get(book_id)
    if existing_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    updates = book_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update",
        )

    updated_book = existing_book.model_copy(update=updates)
    books[book_id] = updated_book
    return updated_book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    del books[book_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
