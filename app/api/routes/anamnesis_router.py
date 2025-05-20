from typing import Dict, List, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models import User
from app.infrastructure.repositories.anamnesis_sqlalchemy import AnamnesisSQLAlchemyRepository
from app.application.use_cases.anamnesis_use_cases import (
    CreateAnamnesisUseCase,
    GetAnamnesisUseCase,
    ListAnamnesisUseCase,
    UpdateAnamnesisUseCase,
    DeleteAnamnesisUseCase
)
from app.schemas.anamnesis_schema import (
    AnamnesisCreate,
    AnamnesisUpdate,
    AnamnesisResponse,
    AnamnesisListResponse
)

# Router aninhado sob patients/{patient_id}/anamneses
router = APIRouter(
    prefix="/patients/{patient_id}/anamneses",
    tags=["anamnesis"],
    responses={404: {"description": "Paciente ou anamnese não encontrado"}},
)

# Dependência para o repositório
def get_anamnesis_repository(db: Session = Depends(get_db)):
    return AnamnesisSQLAlchemyRepository(db)

# Criar anamnese
@router.post("/", response_model=AnamnesisResponse, status_code=201)
async def create_anamnesis(
    patient_id: UUID = Path(..., description="ID do paciente"),
    current_user: User = Depends(get_current_user),
    repo: AnamnesisSQLAlchemyRepository = Depends(get_anamnesis_repository),
    data: AnamnesisCreate = Body(...),
):
    """
    Cria uma nova ficha de anamnese para um paciente.
    
    Requer:
    - ID do paciente
    - Dados da anamnese
    - Usuário autenticado com associação a um assinante
    """
    # Verificação de segurança multi-tenant
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = CreateAnamnesisUseCase(repo)
        result = use_case.execute(data, patient_id, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Obter anamnese específica
@router.get("/{anamnesis_id}", response_model=AnamnesisResponse)
async def get_anamnesis(
    patient_id: UUID = Path(..., description="ID do paciente"),
    anamnesis_id: UUID = Path(..., description="ID da anamnese"),
    current_user: User = Depends(get_current_user),
    repo: AnamnesisSQLAlchemyRepository = Depends(get_anamnesis_repository),
):
    """
    Busca uma ficha de anamnese específica pelo ID.
    
    Requer:
    - ID do paciente
    - ID da anamnese
    - Usuário autenticado com associação a um assinante
    """
    # Verificação de segurança multi-tenant
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = GetAnamnesisUseCase(repo)
        result = use_case.execute(anamnesis_id, current_user.subscriber_id)
        
        # Verificar se a anamnese pertence ao paciente informado
        if result["patient_id"] != patient_id:
            raise HTTPException(
                status_code=404,
                detail="Anamnese não encontrada para este paciente"
            )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Listar anamneses de um paciente
@router.get("/", response_model=AnamnesisListResponse)
async def list_anamnesis(
    patient_id: UUID = Path(..., description="ID do paciente"),
    skip: int = Query(0, ge=0, description="Quantos registros pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros a retornar"),
    current_user: User = Depends(get_current_user),
    repo: AnamnesisSQLAlchemyRepository = Depends(get_anamnesis_repository),
):
    """
    Lista todas as fichas de anamnese de um paciente.
    
    Requer:
    - ID do paciente
    - Usuário autenticado com associação a um assinante
    
    Suporta paginação através dos parâmetros skip e limit.
    """
    # Verificação de segurança multi-tenant
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = ListAnamnesisUseCase(repo)
        return use_case.execute(patient_id, current_user.subscriber_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Atualizar anamnese
@router.put("/{anamnesis_id}", response_model=AnamnesisResponse)
async def update_anamnesis(
    patient_id: UUID = Path(..., description="ID do paciente"),
    anamnesis_id: UUID = Path(..., description="ID da anamnese"),
    current_user: User = Depends(get_current_user),
    repo: AnamnesisSQLAlchemyRepository = Depends(get_anamnesis_repository),
    data: AnamnesisUpdate = Body(...),
):
    """
    Atualiza uma ficha de anamnese existente.
    
    Requer:
    - ID do paciente
    - ID da anamnese
    - Dados da anamnese para atualização
    - Usuário autenticado com associação a um assinante
    """
    # Verificação de segurança multi-tenant
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        # Verificar se a anamnese pertence ao paciente
        check_use_case = GetAnamnesisUseCase(repo)
        anamnesis = check_use_case.execute(anamnesis_id, current_user.subscriber_id)
        
        if anamnesis["patient_id"] != patient_id:
            raise HTTPException(
                status_code=404,
                detail="Anamnese não encontrada para este paciente"
            )
        
        # Atualizar anamnese
        use_case = UpdateAnamnesisUseCase(repo)
        result = use_case.execute(anamnesis_id, data, current_user.subscriber_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Excluir anamnese (logicamente)
@router.delete("/{anamnesis_id}", status_code=204)
async def delete_anamnesis(
    patient_id: UUID = Path(..., description="ID do paciente"),
    anamnesis_id: UUID = Path(..., description="ID da anamnese"),
    current_user: User = Depends(get_current_user),
    repo: AnamnesisSQLAlchemyRepository = Depends(get_anamnesis_repository),
):
    """
    Exclui (logicamente) uma ficha de anamnese.
    
    Requer:
    - ID do paciente
    - ID da anamnese
    - Usuário autenticado com associação a um assinante
    """
    # Verificação de segurança multi-tenant
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        # Verificar se a anamnese pertence ao paciente
        check_use_case = GetAnamnesisUseCase(repo)
        anamnesis = check_use_case.execute(anamnesis_id, current_user.subscriber_id)
        
        if anamnesis["patient_id"] != patient_id:
            raise HTTPException(
                status_code=404,
                detail="Anamnese não encontrada para este paciente"
            )
        
        # Excluir anamnese
        use_case = DeleteAnamnesisUseCase(repo)
        use_case.execute(anamnesis_id, current_user.subscriber_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")