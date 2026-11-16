from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import Base, engine, get_db
from models import Note, User
from schemas import NoteCreate, NoteRead, UserCreate, UserRead
from security import create_access_token, get_current_user, hash_password, verify_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="FastAPI JWT + SQLAlchemy Notes API", lifespan=lifespan)

@app.post("/register", response_model=UserRead, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}

@app.get("/users/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user

@app.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(payload: NoteCreate, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    note = Note(**payload.model_dump(), owner_id=user.id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@app.get("/notes", response_model=list[NoteRead])
async def list_notes(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.owner_id == user.id).order_by(Note.created_at.desc()))
    return result.scalars().all()

@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(note_id: int, payload: NoteCreate, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title, note.content = payload.title, payload.content
    await db.commit()
    await db.refresh(note)
    return note

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.owner_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.commit()

@app.get("/dashboard")
async def dashboard(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.owner_id == user.id))
    return {"message": f"Welcome, {user.username}!", "user_id": user.id,
            "notes_count": len(result.scalars().all())}
