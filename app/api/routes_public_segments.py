"""
Rotas públicas da API para acesso aos segmentos sem autenticação
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.segment import PaginatedSegmentResponse
from app.services.segment_service import SegmentService

# Definir o router
router = APIRouter(
    prefix="/public/segments",
    tags=["public"],
    responses={404: {"description": "Segmento não encontrado"}},
)


@router.get("/", response_model=PaginatedSegmentResponse)
async def list_public_segments(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Quantos segmentos pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de segmentos retornados"),
    nome: Optional[str] = Query(None, description="Filtrar por nome")
):
    """
    Listar todos os segmentos ativos, disponível publicamente para o processo de onboarding.
    Retorna apenas segmentos com is_active=True.
    """
    try:
        # Sempre força o filtro is_active=True para rotas públicas
        filter_params = {"is_active": True}
        
        # Adiciona filtro por nome se fornecido
        if nome is not None:
            filter_params["nome"] = nome
        
        result = SegmentService.get_segments(db, skip, limit, filter_params)
        return result
        
    except Exception as e:
        print(f"[ERROR] Erro ao listar segmentos públicos: {str(e)}")
        raise