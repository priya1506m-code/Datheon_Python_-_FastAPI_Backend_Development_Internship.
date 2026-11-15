from datetime import datetime, timedelta, timezone
from typing import Optional
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be configured in the .env file")

app = FastAPI(title="FastAPI JWT Authentication", version="1.0.0")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Demo-only in-memory storage. Replace with a persistent database in production.
fake_users_db: dict[str, dict[str, str]] = {}


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)


class UserResponse(BaseModel):
    username: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password),
    }
    return {"username": user.username}


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)

    if user is None or not verify_password(
        form_data.password, user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Authenticated successfully",
        "username": current_user["username"],
    }


@app.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Welcome to your dashboard!",
        "user": current_user["username"],
        "data": "This is protected information.",
    }
