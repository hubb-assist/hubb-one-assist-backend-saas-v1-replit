"""
Interfaces para o domínio de Agendamentos (Appointments).
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.domain.appointment.entities import AppointmentEntity


class IAppointmentRepository(ABC):
    """
    Interface para o repositório de Agendamentos.
    
    Define os métodos que qualquer implementação de repositório
    de agendamentos deve fornecer.
    """
    
    @abstractmethod
    def create(self, appointment: AppointmentEntity) -> AppointmentEntity:
        """
        Cria um novo agendamento no repositório.
        
        Args:
            appointment: Entidade de agendamento a ser criada
            
        Returns:
            AppointmentEntity: Entidade criada com ID gerado
            
        Raises:
            ValueError: Se houver conflito de horário ou dados inválidos
        """
        pass
    
    @abstractmethod
    def get_by_id(self, appointment_id: UUID, subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Busca um agendamento por ID.
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante (para isolamento multitenancy)
            
        Returns:
            Optional[AppointmentEntity]: Entidade encontrada ou None se não existir
        """
        pass
    
    @abstractmethod
    def update(self, appointment: AppointmentEntity) -> AppointmentEntity:
        """
        Atualiza um agendamento existente.
        
        Args:
            appointment: Entidade de agendamento com dados atualizados
            
        Returns:
            AppointmentEntity: Entidade atualizada
            
        Raises:
            ValueError: Se o agendamento não existir ou houver conflito de horário
        """
        pass
    
    @abstractmethod
    def delete(self, appointment_id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui (desativa) um agendamento.
        
        Args:
            appointment_id: ID do agendamento a ser excluído
            subscriber_id: ID do assinante (para isolamento multitenancy)
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        pass
    
    @abstractmethod
    def list(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[AppointmentEntity]:
        """
        Lista agendamentos com paginação e filtros.
        
        Args:
            subscriber_id: ID do assinante (para isolamento multitenancy)
            skip: Quantidade de registros para pular (paginação)
            limit: Quantidade máxima de registros para retornar
            filters: Filtros opcionais (patient_id, provider_id, status, date_from, date_to, etc.)
            
        Returns:
            List[AppointmentEntity]: Lista de entidades encontradas
        """
        pass
    
    @abstractmethod
    def count(self, subscriber_id: UUID, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o total de agendamentos, aplicando filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante (para isolamento multitenancy)
            filters: Filtros opcionais (patient_id, provider_id, status, date_from, date_to, etc.)
            
        Returns:
            int: Número total de registros
        """
        pass
    
    @abstractmethod
    def check_conflicts(
        self,
        provider_id: UUID,
        start_time: datetime,
        end_time: datetime,
        appointment_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica se há conflitos de horário para um profissional.
        
        Args:
            provider_id: ID do profissional
            start_time: Horário de início proposto
            end_time: Horário de término proposto
            appointment_id: ID do agendamento atual (para ignorar na verificação em atualizações)
            
        Returns:
            bool: True se houver conflito, False caso contrário
        """
        pass