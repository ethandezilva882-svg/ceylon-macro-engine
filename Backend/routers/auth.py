"""
Backend/routers/auth.py

Register and login endpoints (t2-5). Register auto-issues a token
(matches the User Journey doc: "Submit -> JWT token issued"). Login
returns a generic error on bad credentials, doesn't reveal whether the
email exists or the password was wrong.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.models import User
from Backend.schemas import UserCreate, UserLogin, TokenOut
from Backend.auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/auth/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token, user=user)


@router.post("/auth/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token, user=user)
