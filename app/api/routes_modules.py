"""
Rotas da API para gerenciamento de módulos funcionais
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.module_service import ModuleService
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse, PaginatedModuleResponse

# Criar router
router = APIRouter(
    prefix="/modules",
    tags=["modules"],
    responses={404: {"description": "Módulo não encontrado"}}
)


@router.get("/", response_model=PaginatedModuleResponse)
async def list_modules(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Quantos módulos pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de módulos retornados"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status de ativação")
):
    """
    Listar todos os módulos com opções de paginação e filtros.
    """
    filter_params = {}
    if nome:
        filter_params["nome"] = nome
    if is_active is not None:
        filter_params["is_active"] = is_active
        
    return ModuleService.get_modules(db, skip, limit, filter_params)


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: UUID = Path(..., description="ID do módulo"),
    db: Session = Depends(get_db)
):
    """
    Obter um módulo pelo ID.
    """
    db_module = ModuleService.get_module_by_id(db, module_id)
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo não encontrado"
        )
    return db_module


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db)
):
    """
    Criar um novo módulo.
    """
    return ModuleService.create_module(db, module_data)


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_data: ModuleUpdate,
    module_id: UUID = Path(..., description="ID do módulo"),
    db: Session = Depends(get_db)
):
    """
    Atualizar um módulo existente.
    """
    updated_module = ModuleService.update_module(db, module_id, module_data)
    if not updated_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo não encontrado"
        )
    return updated_module


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: UUID = Path(..., description="ID do módulo"),
    db: Session = Depends(get_db)
):
    """
    Excluir um módulo.
    """
    success = ModuleService.delete_module(db, module_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo não encontrado"
        )
    return None


@router.patch("/{module_id}/activate", response_model=ModuleResponse)
async def activate_module(
    module_id: UUID = Path(..., description="ID do módulo"),
    db: Session = Depends(get_db)
):
    """
    Ativar um módulo.
    """
    updated_module = ModuleService.toggle_module_status(db, module_id, activate=True)
    if not updated_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo não encontrado"
        )
    return updated_module


@router.patch("/{module_id}/deactivate", response_model=ModuleResponse)
async def deactivate_module(
    module_id: UUID = Path(..., description="ID do módulo"),
    db: Session = Depends(get_db)
):
    """
    Desativar um módulo.
    """
    updated_module = ModuleService.toggle_module_status(db, module_id, activate=False)
    if not updated_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Módulo não encontrado"
        )
    return updated_module