"""
Rotas de compatibilidade para lidar com caminhos incorretos ou legados
que o frontend possa estar tentando usar
"""

from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User
from app.services.subscriber_service import SubscriberService

# Criar router separado para rotas de compatibilidade
router = APIRouter(prefix="/api", tags=["compatibility"])

@router.get("/subscribers/", include_in_schema=False)
async def api_subscribers_redirect(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Rota de compatibilidade para /api/subscribers/ 
    Redireciona para a rota correta /subscribers/
    """
    # Pegar query params da requisição original
    params = dict(request.query_params)
    
    # Obter os assinantes diretamente
    result = SubscriberService.get_subscribers(
        db=db, 
        current_user=current_user,
        skip=int(params.get("skip", "0")),
        limit=int(params.get("limit", "10")),
        filter_params={k: v for k, v in params.items() if k not in ["skip", "limit"]}
    )
    
    # Retornar diretamente, evitando redirecionamento 307
    return result

@router.get("/subscribers/{subscriber_id}", include_in_schema=False)
async def api_subscriber_by_id_redirect(
    subscriber_id: str,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Rota de compatibilidade para /api/subscribers/{id}
    Redireciona para a rota correta /subscribers/{id}
    """
    # Converter o ID para UUID para compatibilidade
    from uuid import UUID
    try:
        uuid_id = UUID(subscriber_id)
        # Obter o assinante diretamente
        result = SubscriberService.get_subscriber_by_id(
            db=db, 
            subscriber_id=uuid_id,
            current_user=current_user
        )
    except ValueError:
        # Se o ID não for um UUID válido
        return JSONResponse(
            status_code=400,
            content={
                "detail": f"ID de assinante inválido: {subscriber_id}. Deve ser um UUID válido."
            }
        )
    
    # Retornar diretamente, evitando redirecionamento 307
    return result

@router.get("/subscribers/fallback/", include_in_schema=False)
async def api_subscribers_fallback(
    request: Request
):
    """
    Rota de fallback para quando o frontend tenta usar /api/subscribers/fallback/
    """
    # Retornar uma resposta amigável com instruções de correção
    origin = request.headers.get("Origin", "*")
    
    return JSONResponse(
        status_code=400,
        content={
            "detail": "URL incorreta. Use /subscribers/ em vez de /api/subscribers/fallback/",
            "message": "Por favor, corrija a URL no frontend ou contate o desenvolvedor."
        },
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
        }
    )

@router.get("/external-api/subscribers/", include_in_schema=False)
@router.get("/external-api/subscribers", include_in_schema=False)
async def external_api_subscribers_redirect(
    request: Request
):
    """
    Rota de compatibilidade para /external-api/subscribers/
    """
    # Retornar uma resposta amigável com instruções de correção
    origin = request.headers.get("Origin", "*")
    
    return JSONResponse(
        status_code=400,
        content={
            "detail": "URL incorreta. Use /subscribers/ em vez de /external-api/subscribers/",
            "message": "Por favor, corrija a URL no frontend ou contate o desenvolvedor."
        },
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
        }
    )