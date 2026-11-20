"""Pydantic schemas for OAuth2 token responses and JWT claims."""

from pydantic import BaseModel


class Token(BaseModel):
    """Bearer token response schema."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload decoded from an access token."""

    sub: str | None = None
    exp: int | None = None
    type: str | None = None
