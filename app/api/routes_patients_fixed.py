"""
Rotas da API para gerenciamento de pacientes no sistema HUBB ONE Assist
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.permissions import user_has_permissions
from app.core.role_hierarchy import PERMISSION_CREATE_PATIENT, PERMISSION_VIEW_PATIENT, PERMISSION_EDIT_PATIENT, PERMISSION_DELETE_PATIENT
from app.db.models import User
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientListResponse
from app.services.patient_service import PatientService

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    responses={404: {"description": "Não encontrado"}}
)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo paciente no sistema.
    
    Este endpoint permite o cadastro de um novo paciente, associando-o 
    automaticamente ao assinante (clínica) do usuário atual.
    
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
        
    return PatientService.create_patient(
        db=db,
        patient_data=patient_data,
        subscriber_id=current_user.subscriber_id
    )


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    db: Session = Depends(get_db),
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
        
    return PatientService.list_patients(
        db=db,
        subscriber_id=current_user.subscriber_id,
        skip=skip,
        limit=limit,
        name=name,
        cpf=cpf
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID = Path(..., description="ID do paciente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém detalhes de um paciente específico.
    
    Este endpoint retorna informações detalhadas de um paciente
    pelo seu ID, garantindo que o paciente pertença ao assinante
    do usuário atual.
    
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
        
    return PatientService.get_patient(
        db=db,
        patient_id=patient_id,
        subscriber_id=current_user.subscriber_id
    )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_data: PatientUpdate,
    patient_id: UUID = Path(..., description="ID do paciente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza os dados de um paciente existente.
    
    Este endpoint permite a atualização dos dados de um paciente
    pelo seu ID, garantindo que o paciente pertença ao assinante
    do usuário atual.
    
    É necessário ter a permissão 'CAN_EDIT_PATIENT'.
    """
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem editar pacientes"
        )
        
    return PatientService.update_patient(
        db=db,
        patient_id=patient_id,
        patient_data=patient_data,
        subscriber_id=current_user.subscriber_id
    )


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
async def delete_patient(
    patient_id: UUID = Path(..., description="ID do paciente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove logicamente um paciente do sistema.
    
    Este endpoint marca um paciente como inativo, realizando
    uma deleção lógica (soft delete) em vez de remover fisicamente
    o registro do banco de dados. Garante que o paciente pertença
    ao assinante do usuário atual.
    
    É necessário ter a permissão 'CAN_DELETE_PATIENT'.
    """
    # Verificação de segurança - usuário deve ter um subscriber_id
    if not current_user.subscriber_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários vinculados a um assinante podem remover pacientes"
        )
        
    return PatientService.delete_patient(
        db=db,
        patient_id=patient_id,
        subscriber_id=current_user.subscriber_id
    )