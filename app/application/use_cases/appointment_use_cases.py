"""
Casos de uso para o módulo de Agendamentos
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from app.domain.appointment.entities import Appointment
from app.domain.appointment.interfaces import IAppointmentRepository


class CreateAppointmentUseCase:
    """
    Caso de uso para criar um novo agendamento
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Repositório de agendamentos
        """
        self.repository = repository
    
    def execute(self, data: Dict[str, Any], subscriber_id: UUID) -> Appointment:
        """
        Executa o caso de uso para criar um agendamento
        
        Args:
            data: Dados do agendamento
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Appointment: Entidade criada
            
        Raises:
            ValueError: Se houver erro na validação ou criação
        """
        try:
            # Adicionar o subscriber_id aos dados
            data["subscriber_id"] = subscriber_id
            
            # Criar a entidade de domínio
            appointment = Appointment(**data)
            
            # Persistir no repositório
            return self.repository.create(appointment)
        except Exception as e:
            raise ValueError(f"Erro ao criar agendamento: {str(e)}")


class GetAppointmentUseCase:
    """
    Caso de uso para buscar um agendamento pelo ID
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Repositório de agendamentos
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> Appointment:
        """
        Executa o caso de uso para buscar um agendamento
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Appointment: Entidade encontrada
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        return self.repository.get_by_id(appointment_id, subscriber_id)


class UpdateAppointmentUseCase:
    """
    Caso de uso para atualizar um agendamento existente
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Repositório de agendamentos
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, data: Dict[str, Any], subscriber_id: UUID) -> Appointment:
        """
        Executa o caso de uso para atualizar um agendamento
        
        Args:
            appointment_id: ID do agendamento
            data: Dados a serem atualizados
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Appointment: Entidade atualizada
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou houver erro na validação
        """
        try:
            # Buscar o agendamento existente
            appointment = self.repository.get_by_id(appointment_id, subscriber_id)
            
            # Atualizar os dados
            appointment.update(data)
            
            # Persistir no repositório
            return self.repository.update(appointment)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Erro ao atualizar agendamento: {str(e)}")


class CancelAppointmentUseCase:
    """
    Caso de uso para cancelar um agendamento
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Repositório de agendamentos
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso para cancelar um agendamento
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            bool: True se foi cancelado com sucesso
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou não puder ser cancelado
        """
        try:
            # Buscar o agendamento existente
            appointment = self.repository.get_by_id(appointment_id, subscriber_id)
            
            # Cancelar o agendamento
            appointment.cancel()
            
            # Atualizar no repositório
            self.repository.update(appointment)
            
            return True
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Erro ao cancelar agendamento: {str(e)}")


class ListAppointmentsUseCase:
    """
    Caso de uso para listar agendamentos com filtros
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Repositório de agendamentos
        """
        self.repository = repository
    
    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        patient_id: Optional[UUID] = None,
        provider_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Appointment]:
        """
        Executa o caso de uso para listar agendamentos
        
        Args:
            subscriber_id: ID do assinante (para segurança multi-tenant)
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar
            date_from: Data de início para filtro
            date_to: Data de fim para filtro
            patient_id: ID do paciente para filtro
            provider_id: ID do profissional para filtro
            status: Status do agendamento para filtro
            
        Returns:
            List[Appointment]: Lista de entidades Appointment
        """
        return self.repository.list(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
            patient_id=patient_id,
            provider_id=provider_id,
            status=status
        )