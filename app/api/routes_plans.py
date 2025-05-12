"""
Rotas da API para gerenciamento de planos
"""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import PlanModule, User
from app.services.plan_service import PlanService
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse, PaginatedPlanResponse
from app.core.dependencies import get_current_user, get_current_admin_or_director, get_current_super_admin

# Criar router
router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    responses={404: {"description": "Plano não encontrado"}}
)


@router.get("/", response_model=PaginatedPlanResponse)
async def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
        
    return PlanService.get_plans(db, skip, limit, filter_params, current_user=current_user)


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter um plano pelo ID.
    """
    db_plan = PlanService.get_plan_by_id(db, plan_id, current_user=current_user)
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
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


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
):
    """
    Criar um novo plano.
    """
    db_plan = PlanService.create_plan(db, plan_data)
    
    # Carregar os módulos vinculados ao plano
    plan_modules = db.query(PlanModule).filter(PlanModule.plan_id == db_plan.id).all()
    
    # Converter para schema de resposta
    plan_response = {
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
    
    return plan_response


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_data: PlanUpdate,
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
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
    
    # Carregar os módulos vinculados ao plano
    plan_modules = db.query(PlanModule).filter(PlanModule.plan_id == plan_id).all()
    
    # Converter para schema de resposta
    plan_response = {
        "id": updated_plan.id,
        "name": updated_plan.name,
        "description": updated_plan.description,
        "segment_id": updated_plan.segment_id,
        "base_price": updated_plan.base_price,
        "is_active": updated_plan.is_active,
        "created_at": updated_plan.created_at,
        "updated_at": updated_plan.updated_at,
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
    
    return plan_response


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
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
        
    # Carregar os módulos vinculados ao plano
    plan_modules = db.query(PlanModule).filter(PlanModule.plan_id == plan_id).all()
    
    # Converter para schema de resposta
    plan_response = {
        "id": updated_plan.id,
        "name": updated_plan.name,
        "description": updated_plan.description,
        "segment_id": updated_plan.segment_id,
        "base_price": updated_plan.base_price,
        "is_active": updated_plan.is_active,
        "created_at": updated_plan.created_at,
        "updated_at": updated_plan.updated_at,
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
    
    return plan_response


@router.patch("/{plan_id}/deactivate", response_model=PlanResponse)
async def deactivate_plan(
    plan_id: UUID = Path(..., description="ID do plano"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_director)
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
        
    # Carregar os módulos vinculados ao plano
    plan_modules = db.query(PlanModule).filter(PlanModule.plan_id == plan_id).all()
    
    # Converter para schema de resposta
    plan_response = {
        "id": updated_plan.id,
        "name": updated_plan.name,
        "description": updated_plan.description,
        "segment_id": updated_plan.segment_id,
        "base_price": updated_plan.base_price,
        "is_active": updated_plan.is_active,
        "created_at": updated_plan.created_at,
        "updated_at": updated_plan.updated_at,
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
    
    return plan_response