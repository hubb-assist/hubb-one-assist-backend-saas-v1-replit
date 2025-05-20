"""
Módulo para endpoints de saúde da API
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/", include_in_schema=True)
async def health_check():
    """
    Endpoint de verificação de saúde da API.
    Usado para health checks do Replit e monitoramento.
    """
    return {"status": "ok"}