"""
Interfaces para o módulo de Agendamentos
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.appointment.entities import AppointmentEntity

class IAppointmentRepository(ABC):
    """
    Interface para o repositório de agendamentos
    """
    
    @abstractmethod
    def create(self, data: Dict[str, Any], subscriber_id: UUID) -> AppointmentEntity:
        """
        Cria um novo agendamento
        
        Args:
            data: Dados do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            AppointmentEntity: Entidade de agendamento criada
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Busca um agendamento pelo ID
        
        Args:
            id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AppointmentEntity]: Entidade de agendamento ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def update(self, id: UUID, data: Dict[str, Any], subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Atualiza um agendamento
        
        Args:
            id: ID do agendamento
            data: Dados do agendamento para atualizar
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AppointmentEntity]: Entidade atualizada ou None se não encontrada
        """
        pass
    
    @abstractmethod
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Remove logicamente um agendamento (soft delete)
        
        Args:
            id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def list_all(self, 
                subscriber_id: UUID, 
                skip: int = 0, 
                limit: int = 100,
                date_from: Optional[datetime] = None,
                date_to: Optional[datetime] = None,
                patient_id: Optional[UUID] = None,
                provider_id: Optional[int] = None,
                status: Optional[str] = None) -> List[AppointmentEntity]:
        """
        Lista todos os agendamentos com filtros
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantidade de itens para pular
            limit: Limite de itens por página
            date_from: Data de início para filtro
            date_to: Data de fim para filtro
            patient_id: ID do paciente para filtro
            provider_id: ID do profissional para filtro
            status: Status do agendamento para filtro
            
        Returns:
            List[AppointmentEntity]: Lista de entidades de agendamento
        """
        pass
    
    @abstractmethod
    def check_conflicts(self, 
                        provider_id: int, 
                        start_time: datetime, 
                        end_time: datetime,
                        subscriber_id: UUID,
                        exclude_id: Optional[UUID] = None) -> bool:
        """
        Verifica se há conflitos de horário para um profissional
        
        Args:
            provider_id: ID do profissional
            start_time: Hora de início do agendamento
            end_time: Hora de término do agendamento
            subscriber_id: ID do assinante
            exclude_id: ID do agendamento a ser excluído da verificação (para updates)
            
        Returns:
            bool: True se houver conflito, False caso contrário
        """
        pass