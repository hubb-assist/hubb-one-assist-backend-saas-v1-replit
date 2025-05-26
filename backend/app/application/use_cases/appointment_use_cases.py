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
    Caso de uso para criação de agendamentos
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Implementação de IAppointmentRepository
        """
        self.repository = repository
    
    def execute(self, data: Dict[str, Any], subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - cria um novo agendamento
        
        Args:
            data: Dados do agendamento a ser criado
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário com os dados do agendamento criado
            
        Raises:
            ValueError: Se houver erro de validação ou criação
        """
        try:
            # Garantir que o subscriber_id está correto (segurança multi-tenant)
            data["subscriber_id"] = subscriber_id
            
            # Criar a entidade de domínio
            appointment = Appointment(
                subscriber_id=subscriber_id,
                patient_id=data["patient_id"],
                provider_id=data["provider_id"],
                service_name=data["service_name"],
                start_time=data["start_time"],
                end_time=data["end_time"],
                status=data.get("status", "scheduled"),
                notes=data.get("notes")
            )
            
            # Persistir através do repositório
            created_appointment = self.repository.create(appointment)
            
            # Retornar como dicionário
            return created_appointment.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao criar agendamento: {str(e)}")


class GetAppointmentUseCase:
    """
    Caso de uso para buscar um agendamento por ID
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Implementação de IAppointmentRepository
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - busca um agendamento por ID
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário com os dados do agendamento
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        try:
            # Buscar a entidade através do repositório
            appointment = self.repository.get_by_id(appointment_id, subscriber_id)
            
            # Retornar como dicionário
            return appointment.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao buscar agendamento: {str(e)}")


class UpdateAppointmentUseCase:
    """
    Caso de uso para atualizar um agendamento existente
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Implementação de IAppointmentRepository
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, data: Dict[str, Any], subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - atualiza um agendamento existente
        
        Args:
            appointment_id: ID do agendamento a ser atualizado
            data: Dados a serem atualizados
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário com os dados do agendamento atualizado
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou houver erro de validação
        """
        try:
            # Buscar o agendamento existente
            appointment = self.repository.get_by_id(appointment_id, subscriber_id)
            
            # Atualizar os campos
            appointment.update(data)
            
            # Persistir as alterações
            updated_appointment = self.repository.update(appointment)
            
            # Retornar como dicionário
            return updated_appointment.to_dict()
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
            repository: Implementação de IAppointmentRepository
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso - cancela um agendamento
        
        Args:
            appointment_id: ID do agendamento a ser cancelado
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            bool: True se o cancelamento foi bem-sucedido
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou já estiver concluído
        """
        try:
            # Buscar o agendamento existente
            appointment = self.repository.get_by_id(appointment_id, subscriber_id)
            
            # Cancelar o agendamento (altera o status)
            appointment.cancel()
            
            # Persistir as alterações
            self.repository.update(appointment)
            
            return True
        except Exception as e:
            raise ValueError(f"Erro ao cancelar agendamento: {str(e)}")


class CompleteAppointmentUseCase:
    """
    Caso de uso para marcar um agendamento como concluído
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Implementação de IAppointmentRepository
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - marca um agendamento como concluído
        
        Args:
            appointment_id: ID do agendamento a ser concluído
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário com os dados do agendamento concluído
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou estiver cancelado
        """
        try:
            # Buscar o agendamento existente
            appointment = self.repository.get_by_id(appointment_id, subscriber_id)
            
            # Marcar como concluído
            appointment.complete()
            
            # Persistir as alterações
            updated_appointment = self.repository.update(appointment)
            
            # Retornar como dicionário
            return updated_appointment.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao concluir agendamento: {str(e)}")


class ListAppointmentsUseCase:
    """
    Caso de uso para listar agendamentos com filtros
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Implementação de IAppointmentRepository
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
        provider_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executa o caso de uso - lista agendamentos com filtros
        
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
            List[Dict[str, Any]]: Lista de dicionários com os dados dos agendamentos
        """
        try:
            # Buscar os agendamentos através do repositório
            appointments = self.repository.list(
                subscriber_id=subscriber_id,
                skip=skip,
                limit=limit,
                date_from=date_from,
                date_to=date_to,
                patient_id=patient_id,
                provider_id=provider_id,
                status=status
            )
            
            # Converter para lista de dicionários
            return [appointment.to_dict() for appointment in appointments]
        except Exception as e:
            raise ValueError(f"Erro ao listar agendamentos: {str(e)}")


class DeleteAppointmentUseCase:
    """
    Caso de uso para excluir logicamente um agendamento
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório
        
        Args:
            repository: Implementação de IAppointmentRepository
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso - exclui logicamente um agendamento
        
        Args:
            appointment_id: ID do agendamento a ser excluído
            subscriber_id: ID do assinante (para segurança multi-tenant)
            
        Returns:
            bool: True se a exclusão foi bem-sucedida
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        try:
            # Excluir logicamente através do repositório
            return self.repository.delete(appointment_id, subscriber_id)
        except Exception as e:
            raise ValueError(f"Erro ao excluir agendamento: {str(e)}")