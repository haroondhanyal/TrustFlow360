from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_token, decode_token, fingerprint, hash_password, verify_password
from app.db.session import get_db
from app.models import Organization, RefreshSession, User, now_utc
from app.dependencies import current_user
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserProfileUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_current_user(user: User = Depends(current_user)):
    return user


@router.patch("/me", response_model=UserResponse)
def update_current_user(payload: UserProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value.strip() if field in {"first_name", "last_name"} and value is not None else value)
    db.commit()
    db.refresh(user)
    return user


def issue_tokens(db: Session, user: User) -> TokenResponse:
    access, _ = create_token(user.id, "access", user.organization_id)
    refresh, token_id = create_token(user.id, "refresh", user.organization_id)
    expiry = now_utc() + timedelta(days=get_settings().refresh_token_days)
    db.add(RefreshSession(user_id=user.id, token_id=token_id, token_hash=fingerprint(refresh), expires_at=expiry))
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh, user=UserResponse.model_validate(user), organization=user.organization)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists. Sign in instead.")
    user = User(email=email, first_name=payload.first_name.strip(), last_name=payload.last_name.strip(), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return issue_tokens(db, user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: dict[str, str], db: Session = Depends(get_db)):
    token = payload.get("refresh_token", "")
    try:
        claims = decode_token(token, "refresh")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Refresh session expired. Sign in again") from None
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_id == claims.get("jti")))
    session_expiry = session.expires_at.replace(tzinfo=timezone.utc) if session and session.expires_at.tzinfo is None else session.expires_at if session else None
    if not session or session.revoked_at or session_expiry < now_utc() or session.token_hash != fingerprint(token):
        raise HTTPException(status_code=401, detail="Refresh session expired. Sign in again")
    session.revoked_at = now_utc()
    user = db.get(User, claims["sub"])
    if not user or not user.is_active:
        db.commit()
        raise HTTPException(status_code=401, detail="Account is unavailable")
    return issue_tokens(db, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: dict[str, str], db: Session = Depends(get_db)):
    try:
        claims = decode_token(payload.get("refresh_token", ""), "refresh")
    except jwt.InvalidTokenError:
        return None
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_id == claims.get("jti")))
    if session and not session.revoked_at:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
    return None
