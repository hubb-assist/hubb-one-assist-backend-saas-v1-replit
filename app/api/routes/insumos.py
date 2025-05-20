"""
Rotas da API para o módulo de Insumos.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session
from app.api.deps import (
    get_db, 
    get_current_subscriber_id,
    has_permission,
)
from app.application.use_cases.insumo.create_insumo import CreateInsumoUseCase
from app.application.use_cases.insumo.get_insumo import GetInsumoUseCase
from app.application.use_cases.insumo.update_insumo import UpdateInsumoUseCase
from app.application.use_cases.insumo.delete_insumo import DeleteInsumoUseCase
from app.application.use_cases.insumo.list_insumos import ListInsumosUseCase
from app.domain.insumo.interfaces import InsumoRepositoryInterface
from app.infrastructure.repositories.insumo_repository import InsumoRepository
from app.schemas.insumo import (
    InsumoCreate,
    InsumoResponse,
    InsumoUpdate,
    InsumoListResponse
)
from app.core.exceptions import EntityNotFoundException


router = APIRouter()


def get_insumo_repository(db: Session = Depends(get_db)) -> InsumoRepositoryInterface:
    """Fornece instância de repositório para insumos."""
    return InsumoRepository(db)


@router.post("/", response_model=InsumoResponse, status_code=201)
async def create_insumo(
    insumo_data: InsumoCreate,
    subscriber_id: UUID = Depends(get_current_subscriber_id),
    repository: InsumoRepositoryInterface = Depends(get_insumo_repository),
    _: bool = Depends(has_permission("CAN_CREATE_INSUMO"))
):
    """
    Cria um novo insumo.
    
    Requer permissão: CAN_CREATE_INSUMO
    """
    try:
        use_case = CreateInsumoUseCase(repository)
        result = use_case.execute(
            subscriber_id=subscriber_id,
            nome=insumo_data.nome,
            tipo=insumo_data.tipo,
            unidade=insumo_data.unidade,
            categoria=insumo_data.categoria,
            quantidade=insumo_data.quantidade,
            observacoes=insumo_data.observacoes,
            modulo_id=insumo_data.modulo_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{insumo_id}", response_model=InsumoResponse)
async def get_insumo(
    insumo_id: UUID,
    subscriber_id: UUID = Depends(get_current_subscriber_id),
    repository: InsumoRepositoryInterface = Depends(get_insumo_repository),
    _: bool = Depends(has_permission("CAN_VIEW_INSUMO"))
):
    """
    Obtém um insumo pelo ID.
    
    Requer permissão: CAN_VIEW_INSUMO
    """
    try:
        use_case = GetInsumoUseCase(repository)
        result = use_case.execute(insumo_id, subscriber_id)
        return result
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")


@router.put("/{insumo_id}", response_model=InsumoResponse)
async def update_insumo(
    insumo_id: UUID,
    insumo_data: InsumoUpdate,
    subscriber_id: UUID = Depends(get_current_subscriber_id),
    repository: InsumoRepositoryInterface = Depends(get_insumo_repository),
    _: bool = Depends(has_permission("CAN_UPDATE_INSUMO"))
):
    """
    Atualiza parcialmente um insumo existente.
    
    Requer permissão: CAN_UPDATE_INSUMO
    """
    try:
        use_case = UpdateInsumoUseCase(repository)
        result = use_case.execute(
            insumo_id=insumo_id,
            subscriber_id=subscriber_id,
            nome=insumo_data.nome,
            tipo=insumo_data.tipo,
            unidade=insumo_data.unidade,
            categoria=insumo_data.categoria,
            quantidade=insumo_data.quantidade,
            observacoes=insumo_data.observacoes,
            modulo_id=insumo_data.modulo_id,
            is_active=insumo_data.is_active
        )
        return result
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{insumo_id}", status_code=200)
async def delete_insumo(
    insumo_id: UUID,
    subscriber_id: UUID = Depends(get_current_subscriber_id),
    repository: InsumoRepositoryInterface = Depends(get_insumo_repository),
    _: bool = Depends(has_permission("CAN_DELETE_INSUMO"))
):
    """
    Exclui logicamente um insumo (define is_active=False).
    
    Requer permissão: CAN_DELETE_INSUMO
    """
    try:
        use_case = DeleteInsumoUseCase(repository)
        result = use_case.execute(insumo_id, subscriber_id)
        return result
    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")


@router.get("/", response_model=InsumoListResponse)
async def list_insumos(
    skip: int = Query(0, ge=0, description="Itens para pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de itens a retornar"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    modulo_id: Optional[UUID] = Query(None, description="Filtrar por módulo"),
    is_active: bool = Query(True, description="Filtrar por status (ativo/inativo)"),
    subscriber_id: UUID = Depends(get_current_subscriber_id),
    repository: InsumoRepositoryInterface = Depends(get_insumo_repository),
    _: bool = Depends(has_permission("CAN_LIST_INSUMOS"))
):
    """
    Lista insumos com filtros opcionais.
    
    Requer permissão: CAN_LIST_INSUMOS
    """
    try:
        use_case = ListInsumosUseCase(repository)
        result = use_case.execute(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            categoria=categoria,
            tipo=tipo,
            modulo_id=modulo_id,
            is_active=is_active
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))