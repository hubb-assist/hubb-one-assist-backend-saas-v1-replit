"""
Rotas da API para gerenciamento de pacientes usando a arquitetura DDD.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status

from app.core.dependencies import get_current_user
from app.core.providers import get_patient_repository
from app.core.role_hierarchy import PERMISSION_CREATE_PATIENT, PERMISSION_VIEW_PATIENT, PERMISSION_EDIT_PATIENT, PERMISSION_DELETE_PATIENT
from app.core.permissions import user_has_permissions
from app.db.models import User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
from app.domain.patient.interfaces import PatientRepository
from app.application.use_cases.patient.create_patient import CreatePatientUseCase
from app.application.use_cases.patient.get_patient import GetPatientUseCase
from app.application.use_cases.patient.update_patient import UpdatePatientUseCase
from app.application.use_cases.patient.delete_patient import DeletePatientUseCase
from app.application.use_cases.patient.list_patients import ListPatientsUseCase


router = APIRouter(prefix="/patients-ddd", tags=["patients-ddd"])


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    repository: PatientRepository = Depends(get_patient_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo paciente.
    
    Este endpoint permite criar um novo paciente vinculado ao assinante
    do usuário atual.
    
    É necessário ter a permissão 'CAN_CREATE_PATIENT'.
    """
    # Verificação de permissão
    if not user_has_permissions(current_user, [PERMISSION_CREATE_PATIENT]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você precisa ter permissão de criar pacientes."
        )
        
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem criar pacientes"
        )
        
    # Criar e executar o caso de uso
    use_case = CreatePatientUseCase(repository)
    subscriber_id = UUID(str(current_user.subscriber_id))
    patient = use_case.execute(patient_data, subscriber_id)
    
    # Retornar resposta
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID = Path(..., description="ID do paciente"),
    repository: PatientRepository = Depends(get_patient_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Obter os detalhes de um paciente específico.
    
    Este endpoint retorna os detalhes completos de um paciente 
    vinculado ao assinante do usuário atual.
    
    É necessário ter a permissão 'CAN_VIEW_PATIENT'.
    """
    # Verificação de permissão
    if not user_has_permissions(current_user, [PERMISSION_VIEW_PATIENT]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você precisa ter permissão de visualizar pacientes."
        )
        
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem visualizar pacientes"
        )
        
    # Criar e executar o caso de uso
    use_case = GetPatientUseCase(repository)
    subscriber_id = UUID(str(current_user.subscriber_id))
    patient = use_case.execute(patient_id, subscriber_id)
    
    # Verificar se o paciente foi encontrado
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com ID {patient_id} não encontrado"
        )
        
    # Retornar resposta
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_data: PatientUpdate,
    patient_id: UUID = Path(..., description="ID do paciente"),
    repository: PatientRepository = Depends(get_patient_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar os dados de um paciente existente.
    
    Este endpoint permite atualizar parcial ou totalmente os dados
    de um paciente vinculado ao assinante do usuário atual.
    
    É necessário ter a permissão 'CAN_EDIT_PATIENT'.
    """
    # Verificação de permissão
    if not user_has_permissions(current_user, [PERMISSION_EDIT_PATIENT]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você precisa ter permissão de editar pacientes."
        )
        
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem editar pacientes"
        )
        
    # Criar e executar o caso de uso
    use_case = UpdatePatientUseCase(repository)
    patient = use_case.execute(patient_id, patient_data, current_user.subscriber_id)
    
    # Retornar resposta
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: UUID = Path(..., description="ID do paciente"),
    repository: PatientRepository = Depends(get_patient_repository),
    current_user: User = Depends(get_current_user)
):
    """
    Excluir (desativar) um paciente.
    
    Este endpoint realiza a exclusão lógica de um paciente, 
    marcando-o como inativo mas mantendo seus dados no sistema.
    
    É necessário ter a permissão 'CAN_DELETE_PATIENT'.
    """
    # Verificação de permissão
    if not user_has_permissions(current_user, [PERMISSION_DELETE_PATIENT]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você precisa ter permissão de excluir pacientes."
        )
        
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem excluir pacientes"
        )
        
    # Criar e executar o caso de uso
    use_case = DeletePatientUseCase(repository)
    use_case.execute(patient_id, current_user.subscriber_id)


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    repository: PatientRepository = Depends(get_patient_repository),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Quantos pacientes pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de pacientes a retornar"),
    name: Optional[str] = Query(None, description="Filtrar por nome (contém)"),
    cpf: Optional[str] = Query(None, description="Filtrar por CPF (contém)")
):
    """
    Lista pacientes com opções de paginação e filtros.
    
    Este endpoint retorna uma lista paginada de pacientes vinculados
    ao assinante do usuário atual.
    
    É necessário ter a permissão 'CAN_VIEW_PATIENT'.
    """
    # Verificação de permissão
    if not user_has_permissions(current_user, [PERMISSION_VIEW_PATIENT]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você precisa ter permissão de visualizar pacientes."
        )
        
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem listar pacientes"
        )
        
    # Criar e executar o caso de uso
    use_case = ListPatientsUseCase(repository)
    return use_case.execute(
        subscriber_id=current_user.subscriber_id,
        skip=skip,
        limit=limit,
        name=name,
        cpf=cpf
    )