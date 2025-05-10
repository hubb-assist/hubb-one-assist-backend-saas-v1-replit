"""
Rotas públicas da API para acesso aos planos sem autenticação
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import PlanModule
from app.services.plan_service import PlanService
from app.schemas.plan import PlanResponse, PaginatedPlanResponse

# Criar router
router = APIRouter(
    prefix="/public/plans",
    tags=["public"],
    responses={404: {"description": "Plano não encontrado"}}
)


@router.get("/", response_model=PaginatedPlanResponse)
async def list_public_plans(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Quantos planos pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de planos retornados"),
    name: Optional[str] = Query(None, description="Filtrar por nome"),
    segment_id: Optional[UUID] = Query(None, description="Filtrar por segmento")
):
    """
    Listar todos os planos ativos, disponível publicamente para o processo de onboarding.
    Retorna apenas planos com is_active=True.
    """
    # Sempre força o filtro is_active=True para rotas públicas
    filter_params = {}
    filter_params["is_active"] = True
    
    if name:
        filter_params["name"] = name
    if segment_id:
        filter_params["segment_id"] = segment_id
        
    return PlanService.get_plans(db, skip, limit, filter_params)


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_public_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db)
):
    """
    Obter um plano pelo ID, disponível publicamente para o processo de onboarding.
    Retorna apenas planos com is_active=True.
    """
    db_plan = PlanService.get_plan_by_id(db, plan_id)
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
        
    # Verificar se o plano está ativo
    if db_plan.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado ou inativo"
        )
    
    # Carregar os módulos vinculados ao plano
    plan_modules = db.query(PlanModule).filter(PlanModule.plan_id == plan_id).all()
    
    # Converter para schema de resposta
    plan_data = {
        "id": db_plan.id,
        "name": db_plan.name,
        "description": db_plan.description,
        "segment_id": db_plan.segment_id,
        "base_price": db_plan.base_price,
        "is_active": db_plan.is_active,
        "created_at": db_plan.created_at,
        "updated_at": db_plan.updated_at,
        "modules": [
            {
                "plan_id": pm.plan_id,
                "module_id": pm.module_id,
                "price": pm.price,
                "is_free": pm.is_free,
                "trial_days": pm.trial_days
            } for pm in plan_modules
        ]
    }
    
    return plan_data