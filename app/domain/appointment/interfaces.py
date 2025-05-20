"""
Interfaces para o módulo de Agendamentos
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.domain.appointment.entities import Appointment


class IAppointmentRepository(ABC):
    """
    Interface para o repositório de agendamentos
    
    Define as operações que devem ser implementadas por qualquer repositório
    que trabalhe com a entidade Appointment
    """
    
    @abstractmethod
    def create(self, appointment: Appointment) -> Appointment:
        """
        Cria um novo agendamento no repositório
        
        Args:
            appointment: Entidade Appointment a ser criada
            
        Returns:
            Appointment: Entidade criada com ID gerado
            
        Raises:
            ValueError: Se houver erro na validação ou criação
        """
        pass
    
    @abstractmethod
    def get_by_id(self, appointment_id: UUID, subscriber_id: UUID) -> Appointment:
        """
        Busca um agendamento pelo ID
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante para segurança multi-tenant
            
        Returns:
            Appointment: Entidade encontrada
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        pass
    
    @abstractmethod
    def update(self, appointment: Appointment) -> Appointment:
        """
        Atualiza um agendamento existente
        
        Args:
            appointment: Entidade Appointment com as atualizações
            
        Returns:
            Appointment: Entidade atualizada
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou houver erro na validação
        """
        pass
    
    @abstractmethod
    def delete(self, appointment_id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente um agendamento (define is_active=False)
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante para segurança multi-tenant
            
        Returns:
            bool: True se foi excluído com sucesso, False caso contrário
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        pass
    
    @abstractmethod
    def list(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        patient_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Appointment]:
        """
        Lista agendamentos com filtros opcionais
        
        Args:
            subscriber_id: ID do assinante para segurança multi-tenant
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
        pass