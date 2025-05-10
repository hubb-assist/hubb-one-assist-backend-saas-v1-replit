"""
Rotas da API para gerenciamento de planos
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.plan_service import PlanService
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse, PaginatedPlanResponse

# Criar router
router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    responses={404: {"description": "Plano não encontrado"}}
)


@router.get("/", response_model=PaginatedPlanResponse)
async def list_plans(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Quantos planos pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de planos retornados"),
    name: Optional[str] = Query(None, description="Filtrar por nome"),
    segment_id: Optional[UUID] = Query(None, description="Filtrar por segmento"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os planos com opções de paginação e filtros.
    """
    filter_params = {}
    if name:
        filter_params["name"] = name
    if segment_id:
        filter_params["segment_id"] = segment_id
    if is_active is not None:
        filter_params["is_active"] = is_active
        
    return PlanService.get_plans(db, skip, limit, filter_params)


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db)
):
    """
    Obter um plano pelo ID.
    """
    db_plan = PlanService.get_plan_by_id(db, plan_id)
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
    return db_plan


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db)
):
    """
    Criar um novo plano.
    """
    return PlanService.create_plan(db, plan_data)


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_data: PlanUpdate,
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db)
):
    """
    Atualizar um plano existente.
    """
    updated_plan = PlanService.update_plan(db, plan_id, plan_data)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
    return updated_plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db)
):
    """
    Excluir um plano.
    """
    success = PlanService.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
    return None


@router.patch("/{plan_id}/activate", response_model=PlanResponse)
async def activate_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db)
):
    """
    Ativar um plano.
    """
    updated_plan = PlanService.toggle_plan_status(db, plan_id, activate=True)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
    return updated_plan


@router.patch("/{plan_id}/deactivate", response_model=PlanResponse)
async def deactivate_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db)
):
    """
    Desativar um plano.
    """
    updated_plan = PlanService.toggle_plan_status(db, plan_id, activate=False)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
    return updated_plan