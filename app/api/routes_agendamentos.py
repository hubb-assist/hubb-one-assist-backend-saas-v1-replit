"""
Rotas da API para o módulo de Agendamentos.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User
from app.domain.appointment.entities import AppointmentEntity
from app.infrastructure.repositories.appointment_sqlalchemy import AppointmentRepository
from app.application.use_cases.appointment.create_appointment_use_case import CreateAppointmentUseCase
from app.application.use_cases.appointment.get_appointment_use_case import GetAppointmentUseCase
from app.application.use_cases.appointment.update_appointment_use_case import UpdateAppointmentUseCase
from app.application.use_cases.appointment.cancel_appointment_use_case import CancelAppointmentUseCase
from app.application.use_cases.appointment.list_appointments_use_case import ListAppointmentsUseCase
from app.schemas.appointment_schema import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentPagination
)

router = APIRouter(
    prefix="/agendamentos",
    tags=["Agendamentos"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo agendamento",
    description="Cria um novo agendamento para um paciente com um profissional específico."
)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo agendamento.
    
    Args:
        appointment_data: Dados do agendamento a ser criado
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        AppointmentResponse: Dados do agendamento criado
        
    Raises:
        HTTPException: Se houver conflito de horário ou dados inválidos
    """
    try:
        # Inicializar o repositório e o caso de uso
        repository = AppointmentRepository(db)
        use_case = CreateAppointmentUseCase(repository)
        
        # Executar o caso de uso
        appointment = use_case.execute(
            subscriber_id=current_user.subscriber_id,
            patient_id=appointment_data.patient_id,
            provider_id=appointment_data.provider_id,
            service_id=appointment_data.service_id,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            status=appointment_data.status,
            notes=appointment_data.notes
        )
        
        # Retornar o resultado
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar agendamento: {str(e)}"
        )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Buscar um agendamento por ID",
    description="Retorna os detalhes de um agendamento específico."
)
async def get_appointment(
    appointment_id: UUID = Path(..., description="ID do agendamento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca um agendamento por ID.
    
    Args:
        appointment_id: ID do agendamento
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        AppointmentResponse: Dados do agendamento encontrado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado
    """
    try:
        # Inicializar o repositório e o caso de uso
        repository = AppointmentRepository(db)
        use_case = GetAppointmentUseCase(repository)
        
        # Executar o caso de uso
        appointment = use_case.execute(appointment_id, current_user.subscriber_id)
        
        # Verificar se o agendamento foi encontrado
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agendamento com ID {appointment_id} não encontrado"
            )
        
        # Retornar o resultado
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar agendamento: {str(e)}"
        )


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Atualizar um agendamento",
    description="Atualiza os dados de um agendamento existente."
)
async def update_appointment(
    appointment_data: AppointmentUpdate,
    appointment_id: UUID = Path(..., description="ID do agendamento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um agendamento existente.
    
    Args:
        appointment_data: Dados do agendamento a serem atualizados
        appointment_id: ID do agendamento
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        AppointmentResponse: Dados do agendamento atualizado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado ou houver conflito de horário
    """
    try:
        # Inicializar o repositório e o caso de uso
        repository = AppointmentRepository(db)
        use_case = UpdateAppointmentUseCase(repository)
        
        # Executar o caso de uso
        appointment = use_case.execute(
            appointment_id=appointment_id,
            subscriber_id=current_user.subscriber_id,
            patient_id=appointment_data.patient_id,
            provider_id=appointment_data.provider_id,
            service_id=appointment_data.service_id,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            status=appointment_data.status,
            notes=appointment_data.notes
        )
        
        # Retornar o resultado
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar agendamento: {str(e)}"
        )


@router.delete(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    summary="Cancelar um agendamento",
    description="Cancela um agendamento existente."
)
async def cancel_appointment(
    appointment_id: UUID = Path(..., description="ID do agendamento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancela um agendamento existente.
    
    Args:
        appointment_id: ID do agendamento
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        AppointmentResponse: Dados do agendamento cancelado
        
    Raises:
        HTTPException: Se o agendamento não for encontrado ou não puder ser cancelado
    """
    try:
        # Inicializar o repositório e o caso de uso
        repository = AppointmentRepository(db)
        use_case = CancelAppointmentUseCase(repository)
        
        # Executar o caso de uso
        appointment = use_case.execute(appointment_id, current_user.subscriber_id)
        
        # Retornar o resultado
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cancelar agendamento: {str(e)}"
        )


@router.get(
    "",
    response_model=AppointmentPagination,
    summary="Listar agendamentos",
    description="Lista todos os agendamentos com suporte a paginação e filtros."
)
async def list_appointments(
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros retornados"),
    patient_id: Optional[UUID] = Query(None, description="Filtrar por ID do paciente"),
    provider_id: Optional[UUID] = Query(None, description="Filtrar por ID do profissional"),
    service_id: Optional[UUID] = Query(None, description="Filtrar por ID do serviço"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    date_from: Optional[datetime] = Query(None, description="Filtrar por data inicial"),
    date_to: Optional[datetime] = Query(None, description="Filtrar por data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista agendamentos com paginação e filtros.
    
    Args:
        skip: Quantidade de registros para pular
        limit: Limite de registros retornados
        patient_id: Filtrar por ID do paciente (opcional)
        provider_id: Filtrar por ID do profissional (opcional)
        service_id: Filtrar por ID do serviço (opcional)
        status: Filtrar por status (opcional)
        date_from: Filtrar por data inicial (opcional)
        date_to: Filtrar por data final (opcional)
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        AppointmentPagination: Lista paginada de agendamentos
    """
    try:
        # Inicializar o repositório e o caso de uso
        repository = AppointmentRepository(db)
        use_case = ListAppointmentsUseCase(repository)
        
        # Executar o caso de uso para obter os itens
        appointments = use_case.execute(
            subscriber_id=current_user.subscriber_id,
            skip=skip,
            limit=limit,
            patient_id=patient_id,
            provider_id=provider_id,
            service_id=service_id,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
        
        # Construir os filtros para a contagem total
        filters = {}
        if patient_id:
            filters['patient_id'] = patient_id
        if provider_id:
            filters['provider_id'] = provider_id
        if service_id:
            filters['service_id'] = service_id
        if status:
            filters['status'] = status
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        # Obter a contagem total de registros
        total = repository.count(current_user.subscriber_id, filters)
        
        # Calcular o total de páginas
        pages = (total + limit - 1) // limit if total > 0 else 1
        
        # Montar a resposta paginada
        response = {
            "total": total,
            "items": appointments,
            "page": skip // limit + 1,
            "size": limit,
            "pages": pages
        }
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar agendamentos: {str(e)}"
        )