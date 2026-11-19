"""TEMPORARY dev-only auth helper. Delete once a real login flow exists.

Why this is restricted to app_env == "local":

POST /auth/dev-token hands out a signed, valid access token to ANY caller,
with ANY subject, and no credentials. That is full authentication bypass:
if it were reachable in staging or prod, anyone on the network could mint a
token for any user and read or write every protected resource. The signature
check in get_current_user cannot help, because the token really is signed
with the real jwt_secret.

So the guard is layered:
  1. create_app() only registers this router when app_env == "local".
  2. The handler re-checks and returns 404 otherwise, so a mistake in (1)
     (e.g. someone includes the router unconditionally) still fails closed.
404 rather than 403 so a non-local deployment doesn't even reveal the route.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.config import Settings, get_settings
from app.security import DEFAULT_EXPIRES, create_access_token

router = APIRouter(prefix="/auth", tags=["auth (dev only)"])


class DevTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(default="dev-user", min_length=1, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/dev-token", response_model=TokenResponse)
def dev_token(
    payload: DevTokenRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    if settings.app_env != "local":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not Found")
    token = create_access_token(payload.subject, settings)
    return TokenResponse(
        access_token=token, expires_in=int(DEFAULT_EXPIRES.total_seconds())
    )
