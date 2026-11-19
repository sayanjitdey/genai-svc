from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings

ALGORITHM = "HS256"
DEFAULT_EXPIRES = timedelta(minutes=30)

# auto_error=False so a missing header goes through our 401 (with
# WWW-Authenticate) instead of the framework's default response.
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    subject: str,
    settings: Settings | None = None,
    expires_delta: timedelta = DEFAULT_EXPIRES,
) -> str:
    settings = settings or get_settings()
    now = datetime.now(timezone.utc)
    claims = {"sub": subject, "iat": now, "exp": now + expires_delta}
    return jwt.encode(
        claims, settings.jwt_secret.get_secret_value(), algorithm=ALGORITHM
    )


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    """Validate the Bearer token and return its subject (the user id)."""
    if credentials is None:
        raise _unauthorized("Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token has expired") from None
    except jwt.InvalidTokenError:
        raise _unauthorized("Invalid token") from None
    return str(payload["sub"])
