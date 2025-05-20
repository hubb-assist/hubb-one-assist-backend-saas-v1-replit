"""
Casos de uso para o módulo de Agendamentos
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository

logger = logging.getLogger(__name__)

class CreateAppointmentUseCase:
    """
    Caso de uso para criar um novo agendamento
    """
    
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
    
    def execute(self, data: Dict[str, Any], subscriber_id: UUID) -> AppointmentEntity:
        """
        Executa a criação de um novo agendamento
        
        Args:
            data: Dados do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            AppointmentEntity: Agendamento criado
            
        Raises:
            ValueError: Se houver conflitos de horário ou dados inválidos
        """
        logger.info(f"Iniciando criação de agendamento para subscriber_id={subscriber_id}")
        
        # Validações adicionais podem ser feitas aqui
        if 'start_time' not in data or 'end_time' not in data:
            logger.error("Dados de agendamento incompletos: horários ausentes")
            raise ValueError("Os horários de início e término são obrigatórios")
            
        if data['start_time'] >= data['end_time']:
            logger.error("Validação falhou: horário de início posterior ou igual ao término")
            raise ValueError("O horário de início deve ser anterior ao horário de término")
            
        if 'patient_id' not in data:
            logger.error("Dados de agendamento incompletos: paciente ausente")
            raise ValueError("O ID do paciente é obrigatório")
            
        if 'provider_id' not in data:
            logger.error("Dados de agendamento incompletos: profissional ausente")
            raise ValueError("O ID do profissional é obrigatório")
            
        if 'service_name' not in data:
            logger.error("Dados de agendamento incompletos: serviço ausente")
            raise ValueError("O nome do serviço é obrigatório")
        
        # Criar o agendamento (o repositório já verifica conflitos de horário)
        try:
            appointment = self.repository.create(data, subscriber_id)
            logger.info(f"Agendamento criado com sucesso: {appointment.id}")
            return appointment
        except ValueError as e:
            logger.error(f"Erro ao criar agendamento: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar agendamento: {str(e)}")
            raise ValueError(f"Não foi possível criar o agendamento: {str(e)}")


class GetAppointmentUseCase:
    """
    Caso de uso para buscar um agendamento por ID
    """
    
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
    
    def execute(self, id: UUID, subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Executa a busca de um agendamento por ID
        
        Args:
            id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AppointmentEntity]: Agendamento encontrado ou None
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        logger.info(f"Buscando agendamento id={id} para subscriber_id={subscriber_id}")
        
        appointment = self.repository.get_by_id(id, subscriber_id)
        
        if not appointment:
            logger.warning(f"Agendamento não encontrado: {id}")
            raise ValueError("Agendamento não encontrado")
            
        logger.info(f"Agendamento encontrado: {id}")
        return appointment


class UpdateAppointmentUseCase:
    """
    Caso de uso para atualizar um agendamento existente
    """
    
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
    
    def execute(self, id: UUID, data: Dict[str, Any], subscriber_id: UUID) -> AppointmentEntity:
        """
        Executa a atualização de um agendamento
        
        Args:
            id: ID do agendamento
            data: Dados do agendamento a serem atualizados
            subscriber_id: ID do assinante
            
        Returns:
            AppointmentEntity: Agendamento atualizado
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou houver conflitos
        """
        logger.info(f"Iniciando atualização de agendamento id={id} para subscriber_id={subscriber_id}")
        
        # Validações adicionais podem ser feitas aqui
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                logger.error("Validação falhou: horário de início posterior ou igual ao término")
                raise ValueError("O horário de início deve ser anterior ao horário de término")
        elif 'start_time' in data:
            # Buscar o agendamento atual para verificar com o end_time existente
            current = self.repository.get_by_id(id, subscriber_id)
            if not current:
                logger.error(f"Agendamento não encontrado para atualização: {id}")
                raise ValueError("Agendamento não encontrado")
                
            if data['start_time'] >= current.end_time:
                logger.error("Validação falhou: novo horário de início posterior ou igual ao término atual")
                raise ValueError("O horário de início deve ser anterior ao horário de término")
        elif 'end_time' in data:
            # Buscar o agendamento atual para verificar com o start_time existente
            current = self.repository.get_by_id(id, subscriber_id)
            if not current:
                logger.error(f"Agendamento não encontrado para atualização: {id}")
                raise ValueError("Agendamento não encontrado")
                
            if current.start_time >= data['end_time']:
                logger.error("Validação falhou: horário de início atual posterior ou igual ao novo término")
                raise ValueError("O horário de início deve ser anterior ao horário de término")
        
        # Atualizar o agendamento
        try:
            appointment = self.repository.update(id, data, subscriber_id)
            
            if not appointment:
                logger.error(f"Agendamento não encontrado para atualização: {id}")
                raise ValueError("Agendamento não encontrado")
                
            logger.info(f"Agendamento atualizado com sucesso: {id}")
            return appointment
        except ValueError as e:
            logger.error(f"Erro ao atualizar agendamento: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar agendamento: {str(e)}")
            raise ValueError(f"Não foi possível atualizar o agendamento: {str(e)}")


class CancelAppointmentUseCase:
    """
    Caso de uso para cancelar um agendamento
    """
    
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
    
    def execute(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o cancelamento de um agendamento
        
        Args:
            id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            bool: True se cancelado com sucesso
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        logger.info(f"Iniciando cancelamento de agendamento id={id} para subscriber_id={subscriber_id}")
        
        try:
            # O método delete realiza um soft delete (is_active=False)
            result = self.repository.delete(id, subscriber_id)
            
            if not result:
                logger.error(f"Agendamento não encontrado para cancelamento: {id}")
                raise ValueError("Agendamento não encontrado")
                
            logger.info(f"Agendamento cancelado com sucesso: {id}")
            return True
        except ValueError as e:
            logger.error(f"Erro ao cancelar agendamento: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao cancelar agendamento: {str(e)}")
            raise ValueError(f"Não foi possível cancelar o agendamento: {str(e)}")


class ListAppointmentsUseCase:
    """
    Caso de uso para listar agendamentos com filtros
    """
    
    def __init__(self, repository: IAppointmentRepository):
        self.repository = repository
    
    def execute(self,
               subscriber_id: UUID,
               skip: int = 0,
               limit: int = 100,
               date_from: Optional[datetime] = None,
               date_to: Optional[datetime] = None,
               patient_id: Optional[UUID] = None,
               provider_id: Optional[int] = None,
               status: Optional[str] = None) -> List[AppointmentEntity]:
        """
        Executa a listagem de agendamentos com filtros
        
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
            List[AppointmentEntity]: Lista de agendamentos
        """
        logger.info(f"Listando agendamentos para subscriber_id={subscriber_id} com filtros")
        
        try:
            appointments = self.repository.list_all(
                subscriber_id=subscriber_id,
                skip=skip,
                limit=limit,
                date_from=date_from,
                date_to=date_to,
                patient_id=patient_id,
                provider_id=provider_id,
                status=status
            )
            
            logger.info(f"Listagem de agendamentos concluída: {len(appointments)} encontrados")
            return appointments
        except Exception as e:
            logger.error(f"Erro ao listar agendamentos: {str(e)}")
            raise ValueError(f"Não foi possível listar os agendamentos: {str(e)}")