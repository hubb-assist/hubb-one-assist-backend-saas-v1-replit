"""
Rotas da API para gerenciamento de Insumos.
Parte da camada de apresentação seguindo arquitetura DDD.
"""
from uuid import UUID
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permission
from app.schemas.insumo import InsumoCreate, InsumoUpdate, InsumoResponse
from app.domain.insumo.entities import InsumoEntity
from app.infrastructure.repositories.insumo_repository import InsumoSQLAlchemyRepository
from app.application.use_cases.insumo.create_insumo import CreateInsumoUseCase
from app.application.use_cases.insumo.get_insumo import GetInsumoUseCase
from app.application.use_cases.insumo.update_insumo import UpdateInsumoUseCase
from app.application.use_cases.insumo.delete_insumo import DeleteInsumoUseCase
from app.application.use_cases.insumo.list_insumos import ListInsumosUseCase
from app.infrastructure.adapters.insumo_adapter import InsumoAdapter
from app.db.models.user import User
from app.schemas.common import PaginatedResponse


router = APIRouter()


@router.post("/", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
async def create_insumo(
    insumo_data: InsumoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria um novo insumo.
    
    Requer permissão: CAN_CREATE_INSUMO
    """
    # Verificar permissão
    check_permission(current_user, "CAN_CREATE_INSUMO")
    
    # Inicializar repositório e caso de uso
    repository = InsumoSQLAlchemyRepository(db)
    use_case = CreateInsumoUseCase(repository)
    
    # Executar caso de uso
    insumo_entity = use_case.execute(insumo_data, current_user.subscriber_id)
    
    # Converter para resposta
    return InsumoAdapter.extract_simple_data(insumo_entity)


@router.get("/{insumo_id}", response_model=InsumoResponse)
async def get_insumo(
    insumo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna um insumo pelo ID.
    
    Requer permissão: CAN_VIEW_INSUMO
    """
    # Verificar permissão
    check_permission(current_user, "CAN_VIEW_INSUMO")
    
    # Inicializar repositório e caso de uso
    repository = InsumoSQLAlchemyRepository(db)
    use_case = GetInsumoUseCase(repository)
    
    # Executar caso de uso
    insumo_entity = use_case.execute(insumo_id, current_user.subscriber_id)
    
    # Converter para resposta
    return InsumoAdapter.extract_simple_data(insumo_entity)


@router.put("/{insumo_id}", response_model=InsumoResponse)
async def update_insumo(
    insumo_id: UUID,
    insumo_data: InsumoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza um insumo existente.
    
    Requer permissão: CAN_UPDATE_INSUMO
    """
    # Verificar permissão
    check_permission(current_user, "CAN_UPDATE_INSUMO")
    
    # Inicializar repositório e caso de uso
    repository = InsumoSQLAlchemyRepository(db)
    use_case = UpdateInsumoUseCase(repository)
    
    # Executar caso de uso
    insumo_entity = use_case.execute(insumo_id, insumo_data, current_user.subscriber_id)
    
    # Converter para resposta
    return InsumoAdapter.extract_simple_data(insumo_entity)


@router.delete("/{insumo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insumo(
    insumo_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desativa um insumo logicamente.
    
    Requer permissão: CAN_DELETE_INSUMO
    """
    # Verificar permissão
    check_permission(current_user, "CAN_DELETE_INSUMO")
    
    # Inicializar repositório e caso de uso
    repository = InsumoSQLAlchemyRepository(db)
    use_case = DeleteInsumoUseCase(repository)
    
    # Executar caso de uso
    use_case.execute(insumo_id, current_user.subscriber_id)
    
    # Retornar 204 No Content


@router.get("/", response_model=PaginatedResponse[InsumoResponse])
async def list_insumos(
    categoria: Optional[str] = None,
    modulos: Optional[List[str]] = Query(None),
    tipo: Optional[str] = None,
    nome: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todos os insumos do assinante com paginação e filtros.
    
    Requer permissão: CAN_VIEW_INSUMO
    """
    # Verificar permissão
    check_permission(current_user, "CAN_VIEW_INSUMO")
    
    # Preparar filtros opcionais
    filters = {}
    if categoria:
        filters["categoria"] = categoria
    if modulos:
        filters["modulos"] = modulos
    if tipo:
        filters["tipo"] = tipo
    if nome:
        filters["nome"] = nome
    
    # Inicializar repositório e caso de uso
    repository = InsumoSQLAlchemyRepository(db)
    use_case = ListInsumosUseCase(repository)
    
    # Executar caso de uso
    insumos, total_count = use_case.execute(
        subscriber_id=current_user.subscriber_id,
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    # Converter para resposta
    items = [InsumoAdapter.extract_simple_data(insumo) for insumo in insumos]
    
    # Retornar resposta paginada
    return {
        "items": items,
        "total": total_count,
        "page": skip // limit + 1 if limit > 0 else 1,
        "size": limit,
        "pages": (total_count + limit - 1) // limit if limit > 0 else 1
    }