"""
Rotas da API para gerenciamento de Insumos.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, check_permission
from app.domain.insumo.entities import InsumoEntity
from app.infrastructure.repositories.insumo_repository import InsumoRepositoryImpl
from app.application.use_cases.insumo.create_insumo import CreateInsumoUseCase
from app.application.use_cases.insumo.get_insumo import GetInsumoUseCase
from app.application.use_cases.insumo.update_insumo import UpdateInsumoUseCase
from app.application.use_cases.insumo.delete_insumo import DeleteInsumoUseCase
from app.application.use_cases.insumo.list_insumos import ListInsumosUseCase
from app.db.models.user import User
from app.schemas.insumo import InsumoCreate, InsumoResponse, InsumoUpdate, InsumoList
from app.core.exceptions import EntityNotFoundException

router = APIRouter()


@router.post("/", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
async def create_insumo(
    insumo_data: InsumoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo insumo.
    
    Requer permissão: CAN_CREATE_INSUMO
    """
    # Verificar permissão
    if not check_permission(current_user, "CAN_CREATE_INSUMO"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado para criar insumos"
        )
    
    try:
        # Criar repository e use case
        repository = InsumoRepositoryImpl(db)
        use_case = CreateInsumoUseCase(repository)
        
        # Executar caso de uso
        result = use_case.execute(
            nome=insumo_data.nome,
            tipo=insumo_data.tipo,
            unidade=insumo_data.unidade,
            categoria=insumo_data.categoria,
            quantidade=insumo_data.quantidade,
            observacoes=insumo_data.observacoes,
            modulo_id=insumo_data.modulo_id,
            subscriber_id=current_user.subscriber_id
        )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{insumo_id}", response_model=InsumoResponse)
async def get_insumo(
    insumo_id: UUID = Path(..., description="ID do insumo"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtém um insumo pelo ID.
    
    Requer permissão: CAN_READ_INSUMO
    """
    # Verificar permissão
    if not check_permission(current_user, "CAN_READ_INSUMO"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado para visualizar insumos"
        )
    
    try:
        # Criar repository e use case
        repository = InsumoRepositoryImpl(db)
        use_case = GetInsumoUseCase(repository)
        
        # Executar caso de uso
        result = use_case.execute(insumo_id, current_user.subscriber_id)
        
        return result
    except EntityNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insumo com ID {insumo_id} não encontrado"
        )


@router.patch("/{insumo_id}", response_model=InsumoResponse)
async def update_insumo(
    insumo_data: InsumoUpdate,
    insumo_id: UUID = Path(..., description="ID do insumo"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um insumo existente.
    
    Requer permissão: CAN_UPDATE_INSUMO
    """
    # Verificar permissão
    if not check_permission(current_user, "CAN_UPDATE_INSUMO"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado para atualizar insumos"
        )
    
    try:
        # Criar repository e use case
        repository = InsumoRepositoryImpl(db)
        use_case = UpdateInsumoUseCase(repository)
        
        # Executar caso de uso
        result = use_case.execute(
            insumo_id=insumo_id,
            subscriber_id=current_user.subscriber_id,
            nome=insumo_data.nome,
            tipo=insumo_data.tipo,
            unidade=insumo_data.unidade,
            categoria=insumo_data.categoria,
            quantidade=insumo_data.quantidade,
            observacoes=insumo_data.observacoes,
            modulo_id=insumo_data.modulo_id
        )
        
        return result
    except EntityNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insumo com ID {insumo_id} não encontrado"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{insumo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insumo(
    insumo_id: UUID = Path(..., description="ID do insumo"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Exclui logicamente um insumo (soft delete).
    
    Requer permissão: CAN_DELETE_INSUMO
    """
    # Verificar permissão
    if not check_permission(current_user, "CAN_DELETE_INSUMO"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado para excluir insumos"
        )
    
    try:
        # Criar repository e use case
        repository = InsumoRepositoryImpl(db)
        use_case = DeleteInsumoUseCase(repository)
        
        # Executar caso de uso
        use_case.execute(insumo_id, current_user.subscriber_id)
        
        return None
    except EntityNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insumo com ID {insumo_id} não encontrado"
        )


@router.get("/", response_model=InsumoList)
async def list_insumos(
    nome: Optional[str] = Query(None, description="Filtrar por nome (parcial)"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    modulo_id: Optional[UUID] = Query(None, description="Filtrar por ID do módulo"),
    is_active: Optional[bool] = Query(True, description="Filtrar por status de ativação"),
    skip: int = Query(0, description="Registros a pular (para paginação)"),
    limit: int = Query(100, description="Limite de registros a retornar"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lista insumos com paginação e filtros opcionais.
    
    Requer permissão: CAN_READ_INSUMO
    """
    # Verificar permissão
    if not check_permission(current_user, "CAN_READ_INSUMO"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado para visualizar insumos"
        )
    
    # Criar repository e use case
    repository = InsumoRepositoryImpl(db)
    use_case = ListInsumosUseCase(repository)
    
    # Executar caso de uso
    result = use_case.execute(
        subscriber_id=current_user.subscriber_id,
        skip=skip,
        limit=limit,
        nome=nome,
        tipo=tipo,
        categoria=categoria,
        modulo_id=modulo_id,
        is_active=is_active
    )
    
    return result