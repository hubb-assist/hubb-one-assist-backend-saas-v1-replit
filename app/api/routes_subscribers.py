"""
Rotas da API para gerenciamento de assinantes
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Request, Response
from sqlalchemy.orm import Session

from app.schemas.subscriber import SubscriberCreate, SubscriberUpdate, SubscriberResponse, PaginatedSubscriberResponse
from app.services.subscriber_service import SubscriberService
from app.db.session import get_db
from app.db.models import User
from app.core.dependencies import get_current_user, get_current_super_admin

# Criar router para assinantes
router = APIRouter(
    prefix="/subscribers",
    tags=["subscribers"],
    responses={404: {"description": "Não encontrado"}}
)

@router.get("/", response_model=PaginatedSubscriberResponse, status_code=status.HTTP_200_OK)
async def list_subscribers(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Mudado para get_current_user para permitir acesso baseado em subscriber_id
    skip: int = Query(0, ge=0, description="Quantos assinantes pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de assinantes retornados"),
    name: Optional[str] = Query(None, description="Filtrar por nome do responsável"),
    clinic_name: Optional[str] = Query(None, description="Filtrar por nome da clínica"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    document: Optional[str] = Query(None, description="Filtrar por documento (CPF/CNPJ)"),
    segment_id: Optional[UUID] = Query(None, description="Filtrar por segmento"),
    plan_id: Optional[UUID] = Query(None, description="Filtrar por plano"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os assinantes com opções de paginação e filtros.
    Requer autenticação e filtra automaticamente por subscriber_id para roles não administrativas.
    """
    # Garantir cabeçalhos CORS explicitamente para esta rota
    origin = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    
    # Log para debug
    print(f"Listando assinantes para {current_user.email} com origin: {origin}")
    
    # Montar filtros
    filters = {}
    if name:
        filters["name"] = name
    if clinic_name:
        filters["clinic_name"] = clinic_name
    if email:
        filters["email"] = email
    if document:
        filters["document"] = document
    if segment_id:
        filters["segment_id"] = segment_id
    if plan_id:
        filters["plan_id"] = plan_id
    if is_active is not None:
        filters["is_active"] = is_active
    
    return SubscriberService.get_subscribers(
        db, 
        skip=skip, 
        limit=limit, 
        filter_params=filters,
        current_user=current_user
    )


@router.get("/{subscriber_id}", response_model=SubscriberResponse, status_code=status.HTTP_200_OK)
async def get_subscriber(
    subscriber_id: UUID = Path(..., description="ID do assinante"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Mudado para get_current_user para permitir acesso baseado em subscriber_id
):
    """
    Obter um assinante pelo ID.
    Requer autenticação e filtra automaticamente por subscriber_id para roles não administrativas.
    """
    subscriber = SubscriberService.get_subscriber_by_id(db, subscriber_id, current_user=current_user)
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinante não encontrado"
        )
    return subscriber


@router.post("/", response_model=SubscriberResponse, status_code=status.HTTP_201_CREATED)
async def create_subscriber(
    subscriber_data: SubscriberCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Criar um novo assinante e seu usuário administrador.
    Pode ser acessado sem autenticação para o formulário de onboarding público.
    Se autenticado, requer permissão de SUPER_ADMIN.
    """
    # Verificar permissões se estiver autenticado
    if current_user and current_user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas administradores podem criar assinantes."
        )
    
    return SubscriberService.create_subscriber(db, subscriber_data)


@router.put("/{subscriber_id}", response_model=SubscriberResponse, status_code=status.HTTP_200_OK)
async def update_subscriber(
    subscriber_data: SubscriberUpdate,
    subscriber_id: UUID = Path(..., description="ID do assinante"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Atualizar um assinante existente.
    Requer autenticação como SUPER_ADMIN.
    """
    updated_subscriber = SubscriberService.update_subscriber(db, subscriber_id, subscriber_data)
    if not updated_subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinante não encontrado"
        )
    return updated_subscriber


@router.delete("/{subscriber_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscriber(
    subscriber_id: UUID = Path(..., description="ID do assinante"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Desativar ou excluir um assinante.
    Requer autenticação como SUPER_ADMIN.
    """
    success = SubscriberService.delete_subscriber(db, subscriber_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinante não encontrado"
        )
    return None


@router.patch("/{subscriber_id}/activate", response_model=SubscriberResponse)
async def activate_subscriber(
    subscriber_id: UUID = Path(..., description="ID do assinante"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Ativar um assinante.
    Requer autenticação como SUPER_ADMIN.
    """
    updated_subscriber = SubscriberService.toggle_subscriber_status(db, subscriber_id, activate=True)
    if not updated_subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinante não encontrado"
        )
    return updated_subscriber


@router.patch("/{subscriber_id}/deactivate", response_model=SubscriberResponse)
async def deactivate_subscriber(
    subscriber_id: UUID = Path(..., description="ID do assinante"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Desativar um assinante.
    Requer autenticação como SUPER_ADMIN.
    """
    updated_subscriber = SubscriberService.toggle_subscriber_status(db, subscriber_id, activate=False)
    if not updated_subscriber:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinante não encontrado"
        )
    return updated_subscriber