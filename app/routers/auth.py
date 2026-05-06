from datetime import datetime, UTC, timedelta

from fastapi import Depends, status, HTTPException, APIRouter
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.models import User
from app.schemas import (
    UserRegister,
    UserPublic,
    Token,
)
from app.database import get_session
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register_user(
    data: UserRegister, session: Session = Depends(get_session)
) -> UserPublic:
    user = (
        session.execute(select(User).where(User.email == data.email))
        .scalars()
        .one_or_none()
    )
    if user:
        raise HTTPException(status_code=409, detail=f"Email already in use.")
    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        college=data.college,
        major=data.major,
        degree_type=data.degree_type,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(
    data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)
) -> Token:
    user = (
        session.execute(select(User).where(User.email == data.username))
        .scalars()
        .one_or_none()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    payload = {
        "sub": str(user.id),
        "exp": datetime.now(UTC) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    return Token(access_token=token)


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> UserPublic:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(401, "Could not validate credentials")
    user = (
        session.execute(select(User).where(User.id == user_id)).scalars().one_or_none()
    )
    if user is None:
        raise HTTPException(401, "Could not validate credentials")
    return user


@router.get("/me", response_model=UserPublic)
def get_me(user: User = Depends(get_current_user)):
    return user
