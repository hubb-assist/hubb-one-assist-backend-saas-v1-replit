"""
Rotas da API para o módulo de insumos.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.application.use_cases.insumo.create_insumo import CreateInsumoUseCase
from app.application.use_cases.insumo.get_insumo import GetInsumoUseCase
from app.application.use_cases.insumo.list_insumos import ListInsumosUseCase, ListInsumosByFilterUseCase as ListInsumosBySubscriberUseCase
from app.application.use_cases.insumo.update_insumo import UpdateInsumoUseCase
from app.application.use_cases.insumo.delete_insumo import DeleteInsumoUseCase
from app.application.use_cases.insumo.atualizar_estoque import AtualizarEstoqueUseCase
from app.application.use_cases.insumo.get_movimentacoes import GetMovimentacoesUseCase
from app.infrastructure.repositories.insumo_repository import SQLAlchemyInsumoRepository
from app.schemas.insumo import (
    InsumoCreate,
    InsumoResponse,
    InsumoUpdate,
    InsumoEstoqueMovimento,
    InsumoFilter
)
from app.schemas.insumo_movimentacao import InsumoEstoqueHistoricoRequest


router = APIRouter(prefix="/insumos", tags=["insumos"])


@router.post("/", response_model=InsumoResponse)
def create_insumo(
    insumo_data: InsumoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Cria um novo insumo.
    
    Requer autenticação com um usuário que pertença a um assinante.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Utilizar o subscriber_id do usuário atual, se não foi fornecido explicitamente
    # Cria uma cópia do objeto para não modificar diretamente
    data_dict = insumo_data.dict()
    if not data_dict.get("subscriber_id"):
        data_dict["subscriber_id"] = subscriber_id
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    use_case = CreateInsumoUseCase(repository)
    
    try:
        # Preparar dados para o caso de uso
        data = data_dict  # Usar dados já preparados com subscriber_id
        
        # Garantir que modules_used seja uma lista vazia se for nulo
        modules = getattr(insumo_data, "modules_used", None)
        if modules and isinstance(modules, list):
            data["modules_used"] = [module.dict() for module in modules]
        else:
            data["modules_used"] = []
        
        # Executar o caso de uso
        insumo = use_case.execute(data)
        return insumo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar insumo: {str(e)}")


@router.get("/novo", response_model=Dict[str, Any])
def get_novo_insumo_form(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Retorna dados necessários para o formulário de criação de novo insumo.
    
    Requer autenticação com um usuário que pertença a um assinante.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Retornar estrutura padrão para novo insumo
    return {
        "action": "create",
        "subscriber_id": subscriber_id,
        "categorias_sugeridas": [
            "Medicamentos",
            "Equipamentos",
            "Materiais de Consumo",
            "Produtos de Limpeza",
            "Instrumentos",
            "Outros"
        ],
        "unidades_medida": [
            "UN",
            "KG",
            "G",
            "L",
            "ML",
            "M",
            "CM",
            "MM"
        ]
    }


@router.get("/{insumo_id}", response_model=InsumoResponse)
def get_insumo(
    insumo_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém um insumo específico pelo ID.
    
    Requer autenticação com um usuário que pertença ao mesmo assinante do insumo.
    """
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    use_case = GetInsumoUseCase(repository)
    
    # Executar o caso de uso
    insumo = use_case.execute(insumo_id)
    
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    
    # Verificar se o usuário tem acesso ao insumo
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id or insumo.subscriber_id != subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado a este insumo"
        )
    
    return insumo


@router.get("/", response_model=Dict[str, Any])
def list_insumos(
    skip: int = 0,
    limit: int = 100,
    nome: Optional[str] = None,
    categoria: Optional[str] = None,
    fornecedor: Optional[str] = None,
    estoque_baixo: Optional[bool] = None,
    module_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lista insumos com paginação e filtros opcionais.
    
    Requer autenticação e retorna apenas insumos do assinante do usuário atual.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar filtros a partir dos parâmetros
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
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    use_case = ListInsumosBySubscriberUseCase(repository)
    
    # Executar o caso de uso
    insumos = use_case.execute(
        subscriber_id=subscriber_id, 
        **filters
    )
    
    # Formatar resposta com paginação
    result = {
        "items": insumos[skip:skip+limit],
        "total": len(insumos),
        "skip": skip,
        "limit": limit
    }
    
    return result


@router.put("/{insumo_id}", response_model=InsumoResponse)
def update_insumo(
    insumo_id: UUID,
    insumo_data: InsumoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Atualiza um insumo existente.
    
    Requer autenticação com um usuário que pertença ao mesmo assinante do insumo.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    get_use_case = GetInsumoUseCase(repository)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário
    insumo = get_use_case.execute(insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
        
    if insumo.subscriber_id != subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado a este insumo"
        )
    
    # Criar caso de uso de atualização
    update_use_case = UpdateInsumoUseCase(repository)
    
    # Preparar dados para atualização
    update_data = insumo_data.dict(exclude_unset=True)
    
    # Converter lista de associações de módulos para dicionários se presente
    if "modules_used" in update_data and update_data["modules_used"]:
        update_data["modules_used"] = [module.dict() for module in update_data["modules_used"]]
    
    try:
        # Executar o caso de uso
        updated_insumo = update_use_case.execute(insumo_id, update_data)
        if not updated_insumo:
            raise HTTPException(status_code=404, detail="Insumo não encontrado")
        
        return updated_insumo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar insumo: {str(e)}")


@router.delete("/{insumo_id}", response_model=Dict[str, bool])
def delete_insumo(
    insumo_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Exclui logicamente um insumo (soft delete).
    
    Requer autenticação com um usuário que pertença ao mesmo assinante do insumo.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    get_use_case = GetInsumoUseCase(repository)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário
    insumo = get_use_case.execute(insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
        
    if insumo.subscriber_id != subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado a este insumo"
        )
    
    # Criar caso de uso de exclusão
    delete_use_case = DeleteInsumoUseCase(repository)
    
    # Executar o caso de uso
    result = delete_use_case.execute(insumo_id)
    
    return {"success": result}


@router.post("/{insumo_id}/estoque", response_model=InsumoResponse)
def update_estoque(
    insumo_id: UUID,
    estoque_data: InsumoEstoqueMovimento,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Atualiza o estoque de um insumo (entrada ou saída).
    
    Requer autenticação com um usuário que pertença ao mesmo assinante do insumo.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    get_use_case = GetInsumoUseCase(repository)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário
    insumo = get_use_case.execute(insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
        
    if insumo.subscriber_id != subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado a este insumo"
        )
    
    # Criar caso de uso de atualização de estoque
    estoque_use_case = AtualizarEstoqueUseCase(repository)
    
    try:
        # Executar o caso de uso
        updated_insumo = estoque_use_case.execute(
            insumo_id=insumo_id,
            quantidade=estoque_data.quantidade,
            tipo_movimento=estoque_data.tipo_movimento,
            motivo=getattr(estoque_data, "motivo", None),
            observacao=getattr(estoque_data, "observacao", None),
            usuario_id=getattr(current_user, "id", None)
        )
        
        if not updated_insumo:
            raise HTTPException(status_code=404, detail="Insumo não encontrado")
        
        return updated_insumo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar estoque: {str(e)}")


@router.get("/{insumo_id}/movimentacoes", response_model=Dict[str, Any])
def get_movimentacoes_por_insumo(
    insumo_id: UUID,
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros a retornar"),
    tipo_movimento: Optional[str] = Query(None, pattern=r'^(entrada|saida)$', description="Filtrar por tipo de movimento"),
    data_inicio: Optional[datetime] = Query(None, description="Data inicial para filtro"),
    data_fim: Optional[datetime] = Query(None, description="Data final para filtro"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém o histórico de movimentações de estoque de um insumo específico.
    
    Requer autenticação com um usuário que pertença ao mesmo assinante do insumo.
    Suporta filtros por tipo de movimento e período de datas, além de paginação.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    get_use_case = GetInsumoUseCase(repository)
    
    # Verificar se o insumo existe e pertence ao assinante do usuário
    insumo = get_use_case.execute(insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
        
    if insumo.subscriber_id != subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Acesso não autorizado a este insumo"
        )
    
    # Criar caso de uso para obter histórico de movimentações
    movimentacoes_use_case = GetMovimentacoesUseCase(repository)
    
    try:
        # Executar o caso de uso
        movimentacoes, total = movimentacoes_use_case.execute(
            subscriber_id=subscriber_id,
            insumo_id=insumo_id,
            tipo_movimento=tipo_movimento,
            data_inicio=data_inicio,
            data_fim=data_fim,
            skip=skip,
            limit=limit
        )
        
        # Formatar resposta com paginação
        result = {
            "items": movimentacoes,
            "total": total,
            "skip": skip,
            "limit": limit,
            "insumo": {
                "id": insumo.id,
                "nome": insumo.nome,
                "estoque_atual": insumo.estoque_atual,
                "estoque_minimo": insumo.estoque_minimo,
                "unidade_medida": insumo.unidade_medida
            }
        }
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico de movimentações: {str(e)}")


@router.get("/movimentacoes", response_model=Dict[str, Any])
def get_todas_movimentacoes(
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros a retornar"),
    insumo_id: Optional[UUID] = Query(None, description="Filtrar por ID do insumo"),
    tipo_movimento: Optional[str] = Query(None, pattern=r'^(entrada|saida)$', description="Filtrar por tipo de movimento"),
    data_inicio: Optional[datetime] = Query(None, description="Data inicial para filtro"),
    data_fim: Optional[datetime] = Query(None, description="Data final para filtro"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém o histórico de movimentações de estoque de todos os insumos do assinante.
    
    Requer autenticação e isolamento por multitenancy (subscriber_id).
    Suporta filtros por insumo, tipo de movimento e período de datas, além de paginação.
    """
    # Verificar se o usuário tem acesso
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está associado a um assinante"
        )
    
    # Criar repositório e caso de uso
    repository = SQLAlchemyInsumoRepository(db)
    movimentacoes_use_case = GetMovimentacoesUseCase(repository)
    
    try:
        # Executar o caso de uso
        movimentacoes, total = movimentacoes_use_case.execute(
            subscriber_id=subscriber_id,
            insumo_id=insumo_id,
            tipo_movimento=tipo_movimento,
            data_inicio=data_inicio,
            data_fim=data_fim,
            skip=skip,
            limit=limit
        )
        
        # Formatar resposta com paginação
        result = {
            "items": movimentacoes,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico de movimentações: {str(e)}")