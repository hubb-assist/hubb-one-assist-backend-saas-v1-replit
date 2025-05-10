"""
Rotas da API para gerenciamento de segmentos
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.schemas.segment import SegmentCreate, SegmentUpdate, SegmentResponse, PaginatedSegmentResponse
from app.services.segment_service import SegmentService
from app.core.dependencies import get_current_user, get_current_admin_or_director, get_current_super_admin

# Definir o router
router = APIRouter(
    prefix="/segments",
    tags=["segments"],
    responses={404: {"description": "Segmento não encontrado"}},
)


@router.get("/", response_model=PaginatedSegmentResponse)
async def list_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Quantos segmentos pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de segmentos retornados"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os segmentos com opções de paginação e filtros.
    """
    # Preparar parâmetros de filtro
    filter_params = {}
    if nome is not None:
        filter_params["nome"] = nome
    if is_active is not None:
        filter_params["is_active"] = is_active
    
    return SegmentService.get_segments(db, skip, limit, filter_params)


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: UUID = Path(..., description="ID do segmento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter um segmento pelo ID.
    """
    segment = SegmentService.get_segment_by_id(db, segment_id)
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segmento não encontrado"
        )
    return segment


@router.post("/", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
async def create_segment(
    segment_data: SegmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
):
    """
    Criar um novo segmento.
    """
    return SegmentService.create_segment(db, segment_data)


@router.put("/{segment_id}", response_model=SegmentResponse, status_code=status.HTTP_200_OK)
async def update_segment(
    segment_data: SegmentUpdate,
    segment_id: UUID = Path(..., description="ID do segmento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
):
    """
    Atualizar um segmento existente.
    """
    updated_segment = SegmentService.update_segment(db, segment_id, segment_data)
    if not updated_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segmento não encontrado"
        )
    return updated_segment


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_segment(
    segment_id: UUID = Path(..., description="ID do segmento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Excluir um segmento.
    """
    success = SegmentService.delete_segment(db, segment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segmento não encontrado"
        )
    return None


@router.patch("/{segment_id}/activate", response_model=SegmentResponse)
async def activate_segment(
    segment_id: UUID = Path(..., description="ID do segmento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
):
    """
    Ativar um segmento.
    """
    updated_segment = SegmentService.toggle_segment_status(db, segment_id, activate=True)
    if not updated_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segmento não encontrado"
        )
    return updated_segment


@router.patch("/{segment_id}/deactivate", response_model=SegmentResponse)
async def deactivate_segment(
    segment_id: UUID = Path(..., description="ID do segmento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
):
    """
    Desativar um segmento.
    """
    updated_segment = SegmentService.toggle_segment_status(db, segment_id, activate=False)
    if not updated_segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segmento não encontrado"
        )
    return updated_segment