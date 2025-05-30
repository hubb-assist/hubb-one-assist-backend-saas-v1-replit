"""
Router para endpoints de agendamentos
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.application.use_cases.appointment_use_cases import (
    CreateAppointmentUseCase,
    GetAppointmentUseCase,
    UpdateAppointmentUseCase,
    CancelAppointmentUseCase,
    ListAppointmentsUseCase
)
from app.domain.appointment.interfaces import IAppointmentRepository
from app.infrastructure.repositories.appointment_sqlalchemy import AppointmentSQLAlchemyRepository
from app.db.models import User
from app.schemas.appointment_schema import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate
)

router = APIRouter(
    prefix="/agendamentos",
    tags=["agendamentos"],
    responses={404: {"description": "Agendamento não encontrado"}}
)


def get_repository(db: Session = Depends(get_db)) -> IAppointmentRepository:
    """
    Dependência para obter o repositório de agendamentos
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        IAppointmentRepository: Repositório de agendamentos
    """
    return AppointmentSQLAlchemyRepository(db)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    repository: IAppointmentRepository = Depends(get_repository)
):
    """
    Cria um novo agendamento
    
    Args:
        appointment: Dados do agendamento
        current_user: Usuário autenticado
        repository: Repositório de agendamentos
        
    Returns:
        AppointmentResponse: Agendamento criado
        
    Raises:
        HTTPException: Se houver um erro na criação
    """
    # Verificação de segurança multi-tenant - usuário deve ter um subscriber_id
    if not hasattr(current_user, 'subscriber_id') or not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = CreateAppointmentUseCase(repository)
        subscriber_id = str(current_user.subscriber_id)
        result = use_case.execute(appointment.dict(), UUID(subscriber_id))
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar agendamento: {str(e)}"
        )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    repository: IAppointmentRepository = Depends(get_repository)
):
    """
    Busca um agendamento pelo ID
    
    Args:
        appointment_id: ID do agendamento
        current_user: Usuário autenticado
        repository: Repositório de agendamentos
        
    Returns:
        AppointmentResponse: Agendamento encontrado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado
    """
    # Verificação de segurança multi-tenant - usuário deve ter um subscriber_id
    if not hasattr(current_user, 'subscriber_id') or not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = GetAppointmentUseCase(repository)
        subscriber_id = str(current_user.subscriber_id)
        result = use_case.execute(appointment_id, UUID(subscriber_id))
        return result
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar agendamento: {str(e)}"
        )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    appointment: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    repository: IAppointmentRepository = Depends(get_repository)
):
    """
    Atualiza um agendamento existente
    
    Args:
        appointment_id: ID do agendamento
        appointment: Dados do agendamento a serem atualizados
        current_user: Usuário autenticado
        repository: Repositório de agendamentos
        
    Returns:
        AppointmentResponse: Agendamento atualizado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado ou houver erro na atualização
    """
    # Verificação de segurança multi-tenant - usuário deve ter um subscriber_id
    if not hasattr(current_user, 'subscriber_id') or not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = UpdateAppointmentUseCase(repository)
        subscriber_id = str(current_user.subscriber_id)
        result = use_case.execute(appointment_id, appointment.dict(exclude_unset=True), UUID(subscriber_id))
        return result
    except ValueError as e:
        if "não encontrado" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar agendamento: {str(e)}"
        )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    repository: IAppointmentRepository = Depends(get_repository)
):
    """
    Exclui logicamente um agendamento (is_active=False)
    
    Args:
        appointment_id: ID do agendamento
        current_user: Usuário autenticado
        repository: Repositório de agendamentos
        
    Raises:
        HTTPException: Se o agendamento não for encontrado ou houver erro na exclusão
    """
    # Verificação de segurança multi-tenant - usuário deve ter um subscriber_id
    if not hasattr(current_user, 'subscriber_id') or not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        # Como é uma exclusão lógica, estamos usando o caso de uso de "cancelar" aqui
        use_case = CancelAppointmentUseCase(repository)
        subscriber_id = str(current_user.subscriber_id)
        use_case.execute(appointment_id, UUID(subscriber_id))
    except ValueError as e:
        if "não encontrado" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Agendamento não encontrado"
            )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao excluir agendamento: {str(e)}"
        )


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    patient_id: Optional[UUID] = None,
    provider_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    repository: IAppointmentRepository = Depends(get_repository)
):
    """
    Lista agendamentos com filtros opcionais
    
    Args:
        date_from: Data de início para filtro
        date_to: Data de fim para filtro
        patient_id: ID do paciente para filtro
        provider_id: ID do profissional para filtro
        status: Status do agendamento para filtro
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros para retornar
        current_user: Usuário autenticado
        repository: Repositório de agendamentos
        
    Returns:
        List[AppointmentResponse]: Lista de agendamentos
        
    Raises:
        HTTPException: Se houver um erro na listagem
    """
    # Verificação de segurança multi-tenant - usuário deve ter um subscriber_id
    if not hasattr(current_user, 'subscriber_id') or not current_user.subscriber_id:
        raise HTTPException(
            status_code=403,
            detail="O usuário não está associado a um assinante"
        )
    
    try:
        use_case = ListAppointmentsUseCase(repository)
        subscriber_id = str(current_user.subscriber_id)
        result = use_case.execute(
            subscriber_id=UUID(subscriber_id),
            skip=skip,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
            patient_id=patient_id,
            provider_id=provider_id,
            status=status
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar agendamentos: {str(e)}"
        )