"""
Rotas da API para gerenciamento de usuários
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserUpdate, UserResponse, PaginatedUserResponse
from app.services.user_service import UserService
from app.db.session import get_db
from app.db.models import UserRole

# Criar router para usuários
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Não encontrado"}},
)

@router.get("/", response_model=PaginatedUserResponse, status_code=status.HTTP_200_OK)
async def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Quantos usuários pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de usuários retornados"),
    name: Optional[str] = Query(None, description="Filtrar por nome"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    role: Optional[UserRole] = Query(None, description="Filtrar por role"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os usuários com opções de paginação e filtros.
    """
    # Montar filtros
    filters = {}
    if name:
        filters["name"] = name
    if email:
        filters["email"] = email
    if role:
        filters["role"] = role
    if is_active is not None:
        filters["is_active"] = is_active
    
    return UserService.get_users(db, skip=skip, limit=limit, filter_params=filters)

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db)
):
    """
    Obter um usuário pelo ID.
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Criar um novo usuário.
    """
    return UserService.create_user(db, user_data)

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int = Path(..., description="ID do usuário"),
    user_data: UserUpdate = ...,
    db: Session = Depends(get_db)
):
    """
    Atualizar um usuário existente.
    """
    updated_user = UserService.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int = Path(..., description="ID do usuário"),
    db: Session = Depends(get_db)
):
    """
    Excluir um usuário.
    """
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return None