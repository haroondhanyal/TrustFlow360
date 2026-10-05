import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User

bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue")
    try:
        claims = decode_token(credentials.credentials, "access")
        user = db.get(User, claims["sub"])
    except (jwt.InvalidTokenError, KeyError):
        user = None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session is invalid or expired")
    claim_org = claims.get("org") if "claims" in locals() else None
    if claim_org != user.organization_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session is out of date. Sign in again")
    return user
