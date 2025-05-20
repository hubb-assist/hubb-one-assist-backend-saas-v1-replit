"""
Esquemas Pydantic para tokens de autenticação.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    """Esquema para retorno de token de acesso."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Esquema para payload do token JWT."""
    sub: Optional[UUID] = None
    role: Optional[str] = None
    subscriber_id: Optional[UUID] = None
    segment_id: Optional[UUID] = None
    permissions: Optional[dict] = None