"""
Rotas públicas específicas para garantir que o CORS funcione com subscribers
"""

from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User

# Criar router separado para rotas públicas CORS
router = APIRouter(
    prefix="/subscribers-cors",
    tags=["subscribers-cors"],
    include_in_schema=False  # Não mostrar na documentação
)

@router.get("/")
@router.options("/")
async def cors_subscribers_endpoint(
    request: Request
):
    """
    Endpoint CORS público para garantir que o frontend possa
    verificar se os cabeçalhos CORS estão funcionando.
    """
    # Pegar a origem
    origin = request.headers.get("Origin", "*")
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "CORS está configurado corretamente",
            "origin": origin,
            "details": "Use esta resposta para confirmar que os cabeçalhos CORS estão funcionando"
        },
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "86400"  # Cache preflight por 24 horas
        }
    )