from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models import User
from app.schemas.cost_fixed import (
    CostFixedCreate, 
    CostFixedUpdate, 
    CostFixedResponse, 
    CostFixedListResponse
)
from app.domain.cost_fixed.entities import CostFixedEntity
from app.infrastructure.repositories.cost_fixed_repository import CostFixedSQLAlchemyRepository
from app.application.use_cases.cost_fixed.create_cost_fixed import CreateCostFixedUseCase
from app.application.use_cases.cost_fixed.get_cost_fixed import GetCostFixedUseCase
from app.application.use_cases.cost_fixed.update_cost_fixed import UpdateCostFixedUseCase
from app.application.use_cases.cost_fixed.delete_cost_fixed import DeleteCostFixedUseCase
from app.application.use_cases.cost_fixed.list_cost_fixed import ListCostFixedUseCase


router = APIRouter(
    prefix="/custos/fixos",
    tags=["custos"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=CostFixedResponse)
async def create_cost_fixed(
    cost_fixed_create: CostFixedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo custo fixo para o assinante do usuário logado.
    """
    # Verifica se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(status_code=400, detail="Usuário não está associado a um assinante")
    
    # Inicializa o repositório e o caso de uso
    repository = CostFixedSQLAlchemyRepository(db)
    use_case = CreateCostFixedUseCase(repository)
    
    try:
        # Executa o caso de uso
        cost_fixed = use_case.execute(
            nome=cost_fixed_create.nome,
            valor=cost_fixed_create.valor,
            data=cost_fixed_create.data,
            subscriber_id=subscriber_id,
            observacoes=cost_fixed_create.observacoes
        )
        
        return cost_fixed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@router.get("/", response_model=CostFixedListResponse)
async def list_costs_fixed(
    skip: int = Query(0, ge=0, description="Quantos itens pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de itens a retornar (paginação)"),
    date_from: Optional[date] = Query(None, description="Data inicial para filtro"),
    date_to: Optional[date] = Query(None, description="Data final para filtro"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista custos fixos do assinante do usuário logado, com opção de filtro por data.
    """
    # Verifica se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(status_code=400, detail="Usuário não está associado a um assinante")
    
    # Inicializa o repositório e o caso de uso
    repository = CostFixedSQLAlchemyRepository(db)
    use_case = ListCostFixedUseCase(repository)
    
    try:
        # Executa o caso de uso
        items, total = use_case.execute(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            date_from=date_from,
            date_to=date_to
        )
        
        # Monta a resposta paginada
        return CostFixedListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@router.get("/{cost_fixed_id}", response_model=CostFixedResponse)
async def get_cost_fixed(
    cost_fixed_id: UUID = Path(..., description="ID do custo fixo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém um custo fixo específico pelo seu ID.
    """
    # Verifica se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(status_code=400, detail="Usuário não está associado a um assinante")
    
    # Inicializa o repositório e o caso de uso
    repository = CostFixedSQLAlchemyRepository(db)
    use_case = GetCostFixedUseCase(repository)
    
    try:
        # Executa o caso de uso
        cost_fixed = use_case.execute(cost_fixed_id=cost_fixed_id, subscriber_id=subscriber_id)
        
        if not cost_fixed:
            raise HTTPException(status_code=404, detail=f"Custo fixo com ID {cost_fixed_id} não encontrado")
            
        return cost_fixed
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@router.put("/{cost_fixed_id}", response_model=CostFixedResponse)
async def update_cost_fixed(
    cost_fixed_id: UUID = Path(..., description="ID do custo fixo"),
    cost_fixed_update: CostFixedUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um custo fixo existente.
    """
    # Verifica se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(status_code=400, detail="Usuário não está associado a um assinante")
    
    # Inicializa o repositório e o caso de uso
    repository = CostFixedSQLAlchemyRepository(db)
    use_case = UpdateCostFixedUseCase(repository)
    
    try:
        # Converte o modelo Pydantic para dicionário, filtrando valores None
        update_data = cost_fixed_update.model_dump(exclude_unset=True, exclude_none=True)
        
        # Executa o caso de uso
        updated_cost_fixed = use_case.execute(
            cost_fixed_id=cost_fixed_id,
            subscriber_id=subscriber_id,
            update_data=update_data
        )
        
        if not updated_cost_fixed:
            raise HTTPException(status_code=404, detail=f"Custo fixo com ID {cost_fixed_id} não encontrado")
            
        return updated_cost_fixed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@router.delete("/{cost_fixed_id}", response_model=dict)
async def delete_cost_fixed(
    cost_fixed_id: UUID = Path(..., description="ID do custo fixo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui (desativa) um custo fixo.
    """
    # Verifica se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(status_code=400, detail="Usuário não está associado a um assinante")
    
    # Inicializa o repositório e o caso de uso
    repository = CostFixedSQLAlchemyRepository(db)
    use_case = DeleteCostFixedUseCase(repository)
    
    try:
        # Executa o caso de uso
        result = use_case.execute(cost_fixed_id=cost_fixed_id, subscriber_id=subscriber_id)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Custo fixo com ID {cost_fixed_id} não encontrado")
            
        return {"success": True, "message": "Custo fixo excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")