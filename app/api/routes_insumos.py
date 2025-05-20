"""
Rotas da API para gerenciamento de Insumos.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.permissions import has_permission
from app.db.models import User
from app.domain.insumo.entities import InsumoEntity
from app.schemas.insumo import (
    InsumoCreate, InsumoUpdate, InsumoResponse, InsumoListResponse
)
from app.infrastructure.repositories.insumo_repository import SQLAlchemyInsumoRepository
from app.application.use_cases.insumo.create_insumo import CreateInsumoUseCase
from app.application.use_cases.insumo.get_insumo import GetInsumoUseCase
from app.application.use_cases.insumo.list_insumos import ListInsumosUseCase
from app.application.use_cases.insumo.update_insumo import UpdateInsumoUseCase
from app.application.use_cases.insumo.delete_insumo import DeleteInsumoUseCase
from app.application.use_cases.insumo.atualizar_estoque import AtualizarEstoqueInsumoUseCase

# Criar o router para insumos
router = APIRouter(prefix="/insumos", tags=["insumos"])


@router.get("", response_model=InsumoListResponse)
async def list_insumos(
    skip: int = Query(0, ge=0, description="Quantos insumos pular (paginação)"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de insumos retornados"),
    nome: Optional[str] = Query(None, description="Filtrar por nome (parcial)"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    fornecedor: Optional[str] = Query(None, description="Filtrar por fornecedor (parcial)"),
    estoque_baixo: Optional[bool] = Query(None, description="Filtrar apenas insumos com estoque abaixo do mínimo"),
    module_id: Optional[UUID] = Query(None, description="Filtrar insumos associados a um módulo específico"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista insumos com opções de paginação e filtros.
    Requer autenticação.
    """
    # Verificar permissão
    if not has_permission(current_user, "insumos:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para listar insumos"
        )
    
    # Construir filtros a partir dos parâmetros
    filters = {}
    if nome:
        filters["nome"] = nome
    if categoria:
        filters["categoria"] = categoria
    if fornecedor:
        filters["fornecedor"] = fornecedor
    if estoque_baixo is not None:
        filters["estoque_baixo"] = estoque_baixo
    if module_id:
        filters["module_id"] = module_id
    
    # Instanciar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    use_case = ListInsumosUseCase(repository)
    
    # Executar caso de uso com controle multitenant
    subscriber_id = current_user.subscriber_id if current_user.role != "SUPER_ADMIN" else None
    result = use_case.execute(skip=skip, limit=limit, subscriber_id=subscriber_id, filters=filters)
    
    # Transformar entidades em resposta da API
    return {
        "items": [
            {
                **vars(item),
                "estoque_baixo": item.verificar_estoque_baixo(),
                "valor_total_estoque": float(item.calcular_valor_total())
            }
            for item in result["items"]
        ],
        "total": result["total"],
        "skip": result["skip"],
        "limit": result["limit"]
    }


@router.get("/{insumo_id}", response_model=InsumoResponse)
async def get_insumo(
    insumo_id: UUID = Path(..., description="ID do insumo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém detalhes de um insumo pelo ID.
    Requer autenticação.
    """
    # Verificar permissão
    if not has_permission(current_user, "insumos:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para visualizar insumos"
        )
    
    # Instanciar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    use_case = GetInsumoUseCase(repository)
    
    # Executar caso de uso
    insumo = use_case.execute(insumo_id=insumo_id)
    
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insumo não encontrado"
        )
    
    # Verificar se o usuário tem acesso a este insumo (multitenant)
    if current_user.role != "SUPER_ADMIN" and insumo.subscriber_id != current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para acessar este insumo"
        )
    
    # Transformar entidade em resposta da API
    return {
        **vars(insumo),
        "estoque_baixo": insumo.verificar_estoque_baixo(),
        "valor_total_estoque": float(insumo.calcular_valor_total())
    }


@router.post("", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
async def create_insumo(
    insumo_data: InsumoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo insumo.
    Requer autenticação e permissão específica.
    """
    # Verificar permissão
    if not has_permission(current_user, "insumos:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para criar insumos"
        )
    
    # Definir subscriber_id com base no usuário atual (multitenant)
    subscriber_id = current_user.subscriber_id
    if not subscriber_id and current_user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário sem assinante associado não pode criar insumos"
        )
    
    # Usar subscriber_id do payload apenas para admin, senão usar o do usuário
    if current_user.role != "SUPER_ADMIN":
        insumo_data.subscriber_id = subscriber_id
    
    # Instanciar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    use_case = CreateInsumoUseCase(repository)
    
    # Executar caso de uso
    try:
        insumo = use_case.execute(
            nome=insumo_data.nome,
            descricao=insumo_data.descricao,
            categoria=insumo_data.categoria,
            valor_unitario=insumo_data.valor_unitario,
            unidade_medida=insumo_data.unidade_medida,
            estoque_minimo=insumo_data.estoque_minimo,
            estoque_atual=insumo_data.estoque_atual,
            subscriber_id=insumo_data.subscriber_id,
            fornecedor=insumo_data.fornecedor,
            codigo_referencia=insumo_data.codigo_referencia,
            data_validade=insumo_data.data_validade,
            data_compra=insumo_data.data_compra,
            observacoes=insumo_data.observacoes,
            modules_used=insumo_data.modules_used
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar insumo: {str(e)}"
        )
    
    # Transformar entidade em resposta da API
    return {
        **vars(insumo),
        "estoque_baixo": insumo.verificar_estoque_baixo(),
        "valor_total_estoque": float(insumo.calcular_valor_total())
    }


@router.put("/{insumo_id}", response_model=InsumoResponse)
async def update_insumo(
    insumo_data: InsumoUpdate,
    insumo_id: UUID = Path(..., description="ID do insumo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um insumo existente.
    Requer autenticação e permissão específica.
    """
    # Verificar permissão
    if not has_permission(current_user, "insumos:update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para atualizar insumos"
        )
    
    # Instanciar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário (multitenant)
    get_use_case = GetInsumoUseCase(repository)
    insumo = get_use_case.execute(insumo_id=insumo_id)
    
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insumo não encontrado"
        )
    
    # Verificar se o usuário tem acesso a este insumo (multitenant)
    if current_user.role != "SUPER_ADMIN" and insumo.subscriber_id != current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para acessar este insumo"
        )
    
    # Converter dados do Pydantic para dicionário, excluindo valores None
    update_data = {k: v for k, v in insumo_data.dict().items() if v is not None}
    
    # Executar caso de uso de atualização
    update_use_case = UpdateInsumoUseCase(repository)
    updated_insumo = update_use_case.execute(insumo_id=insumo_id, data=update_data)
    
    if not updated_insumo:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar insumo"
        )
    
    # Transformar entidade em resposta da API
    return {
        **vars(updated_insumo),
        "estoque_baixo": updated_insumo.verificar_estoque_baixo(),
        "valor_total_estoque": float(updated_insumo.calcular_valor_total())
    }


@router.delete("/{insumo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insumo(
    insumo_id: UUID = Path(..., description="ID do insumo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui logicamente um insumo (soft delete).
    Requer autenticação e permissão específica.
    """
    # Verificar permissão
    if not has_permission(current_user, "insumos:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para excluir insumos"
        )
    
    # Instanciar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário (multitenant)
    get_use_case = GetInsumoUseCase(repository)
    insumo = get_use_case.execute(insumo_id=insumo_id)
    
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insumo não encontrado"
        )
    
    # Verificar se o usuário tem acesso a este insumo (multitenant)
    if current_user.role != "SUPER_ADMIN" and insumo.subscriber_id != current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para acessar este insumo"
        )
    
    # Executar caso de uso de exclusão
    delete_use_case = DeleteInsumoUseCase(repository)
    success = delete_use_case.execute(insumo_id=insumo_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir insumo"
        )


@router.post("/{insumo_id}/estoque", response_model=InsumoResponse)
async def atualizar_estoque(
    insumo_id: UUID = Path(..., description="ID do insumo"),
    quantidade: int = Body(..., description="Quantidade a adicionar (positiva) ou remover (negativa)"),
    observacao: Optional[str] = Body(None, description="Observação opcional sobre a movimentação"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza o estoque de um insumo (adiciona ou remove quantidade).
    Requer autenticação e permissão específica.
    """
    # Verificar permissão
    if not has_permission(current_user, "insumos:update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para atualizar estoque de insumos"
        )
    
    # Instanciar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário (multitenant)
    get_use_case = GetInsumoUseCase(repository)
    insumo = get_use_case.execute(insumo_id=insumo_id)
    
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insumo não encontrado"
        )
    
    # Verificar se o usuário tem acesso a este insumo (multitenant)
    if current_user.role != "SUPER_ADMIN" and insumo.subscriber_id != current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não possui permissão para acessar este insumo"
        )
    
    # Executar caso de uso de atualização de estoque
    estoque_use_case = AtualizarEstoqueInsumoUseCase(repository)
    success, updated_insumo, message = estoque_use_case.execute(
        insumo_id=insumo_id,
        quantidade=quantidade,
        observacao=observacao
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Transformar entidade em resposta da API
    return {
        **vars(updated_insumo),
        "estoque_baixo": updated_insumo.verificar_estoque_baixo(),
        "valor_total_estoque": float(updated_insumo.calcular_valor_total())
    }