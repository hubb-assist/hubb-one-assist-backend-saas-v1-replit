from typing import Optional, Dict, Any
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.custo_clinico import CustoClinicalCreate, CustoClinicalUpdate, CustoClinicalResponse, CustoClinicalList
from app.domain.cost_clinical.interfaces import ICostClinicalRepository
from app.infrastructure.repositories.cost_clinical_repository import CostClinicalSQLAlchemyRepository
from app.application.use_cases.cost_clinical.create_cost_clinical import CreateCostClinicalUseCase
from app.application.use_cases.cost_clinical.get_cost_clinical import GetCostClinicalUseCase
from app.application.use_cases.cost_clinical.update_cost_clinical import UpdateCostClinicalUseCase
from app.application.use_cases.cost_clinical.delete_cost_clinical import DeleteCostClinicalUseCase
from app.application.use_cases.cost_clinical.list_cost_clinical import ListCostClinicalUseCase

# Criar o router
router = APIRouter(
    prefix="/custos/clinicos",
    tags=["custos"],
    responses={404: {"description": "Not found"}}
)

def get_repository(db: Session = Depends(get_db)) -> ICostClinicalRepository:
    """
    Retorna uma instância do repositório de custos clínicos.
    """
    return CostClinicalSQLAlchemyRepository(db)

@router.get("/", response_model=CustoClinicalList)
async def list_custos_clinicos(
    skip: int = Query(0, ge=0, description="Quantos registros pular (paginação)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros a retornar"),
    date_from: Optional[date] = Query(None, description="Data inicial para filtro (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Data final para filtro (YYYY-MM-DD)"),
    repository: ICostClinicalRepository = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    """
    Retorna uma lista paginada de custos clínicos do assinante do usuário atual.
    Opcionalmente filtra por intervalo de datas.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        return CustoClinicalList(items=[], total=0, skip=skip, limit=limit)
    
    # Executar o caso de uso
    use_case = ListCostClinicalUseCase(repository)
    result = use_case.execute(
        subscriber_id=subscriber_id,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to
    )
    
    # Converter para o esquema de resposta
    items = [CustoClinicalResponse.model_validate(entity.to_dict()) for entity in result["items"]]
    
    return CustoClinicalList(
        items=items,
        total=result["total"],
        skip=result["skip"],
        limit=result["limit"]
    )

@router.get("/{custo_clinico_id}", response_model=CustoClinicalResponse)
async def get_custo_clinico(
    custo_clinico_id: UUID = Path(..., description="ID do custo clínico"),
    repository: ICostClinicalRepository = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    """
    Retorna os detalhes de um custo clínico específico.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Executar o caso de uso
    use_case = GetCostClinicalUseCase(repository)
    custo_clinico = use_case.execute(
        id=custo_clinico_id,
        subscriber_id=subscriber_id
    )
    
    if not custo_clinico:
        raise HTTPException(status_code=404, detail="Custo clínico não encontrado")
        
    # Converter para o esquema de resposta
    return CustoClinicalResponse.model_validate(custo_clinico.to_dict())

@router.post("/", response_model=CustoClinicalResponse)
async def create_custo_clinico(
    custo_clinico: CustoClinicalCreate,
    repository: ICostClinicalRepository = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    """
    Cria um novo custo clínico para o assinante do usuário atual.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    try:
        # Executar o caso de uso
        use_case = CreateCostClinicalUseCase(repository)
        result = use_case.execute(
            data=custo_clinico,
            subscriber_id=subscriber_id
        )
        
        # Converter para o esquema de resposta
        return CustoClinicalResponse.model_validate(result.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao criar custo clínico: {str(e)}"
        )

@router.put("/{custo_clinico_id}", response_model=CustoClinicalResponse)
async def update_custo_clinico(
    custo_clinico_id: UUID,
    custo_clinico: CustoClinicalUpdate,
    repository: ICostClinicalRepository = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    """
    Atualiza um custo clínico existente.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Verificar se pelo menos um campo para atualização foi fornecido
    update_data = custo_clinico.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="Pelo menos um campo deve ser fornecido para atualização"
        )
    
    try:
        # Executar o caso de uso
        use_case = UpdateCostClinicalUseCase(repository)
        result = use_case.execute(
            id=custo_clinico_id,
            data=custo_clinico,
            subscriber_id=subscriber_id
        )
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail="Custo clínico não encontrado"
            )
            
        # Converter para o esquema de resposta
        return CustoClinicalResponse.model_validate(result.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erro ao atualizar custo clínico: {str(e)}"
        )

@router.delete("/{custo_clinico_id}")
async def delete_custo_clinico(
    custo_clinico_id: UUID,
    repository: ICostClinicalRepository = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    """
    Remove (desativa) um custo clínico.
    """
    # Verificar se o usuário está associado a um assinante
    subscriber_id = getattr(current_user, "subscriber_id", None)
    if not subscriber_id:
        raise HTTPException(
            status_code=400, 
            detail="Usuário não está associado a um assinante"
        )
    
    # Executar o caso de uso
    use_case = DeleteCostClinicalUseCase(repository)
    result = use_case.execute(
        id=custo_clinico_id,
        subscriber_id=subscriber_id
    )
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail="Custo clínico não encontrado"
        )
        
    return {"success": True, "message": "Custo clínico removido com sucesso"}