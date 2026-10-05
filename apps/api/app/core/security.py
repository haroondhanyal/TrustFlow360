from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)


def fingerprint(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def create_token(subject: str, token_type: str, organization_id: str | None = None) -> tuple[str, str]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    token_id = str(uuid4())
    duration = timedelta(minutes=settings.access_token_minutes) if token_type == "access" else timedelta(days=settings.refresh_token_days)
    payload = {"sub": subject, "typ": token_type, "jti": token_id, "iat": now, "exp": now + duration}
    if organization_id:
        payload["org"] = organization_id
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256"), token_id


def decode_token(token: str, expected_type: str) -> dict:
    claims = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    if claims.get("typ") != expected_type:
        raise jwt.InvalidTokenError("Wrong token type")
    return claims
