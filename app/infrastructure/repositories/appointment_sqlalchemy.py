"""
Implementação do repositório de agendamentos usando SQLAlchemy
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
import logging
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository
from app.db.models_appointment import Appointment

class AppointmentSQLAlchemyRepository(IAppointmentRepository):
    """
    Implementação do repositório de agendamentos usando SQLAlchemy
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def _model_to_entity(self, model: Appointment) -> AppointmentEntity:
        """
        Converte um modelo SQLAlchemy para entidade de domínio
        
        Args:
            model: Modelo SQLAlchemy
            
        Returns:
            AppointmentEntity: Entidade de domínio
        """
        return AppointmentEntity(
            id=model.id,
            subscriber_id=model.subscriber_id,
            patient_id=model.patient_id,
            provider_id=model.provider_id,
            service_name=model.service_name,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            notes=model.notes,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def create(self, data: Dict[str, Any], subscriber_id: UUID) -> AppointmentEntity:
        """
        Cria um novo agendamento
        
        Args:
            data: Dados do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            AppointmentEntity: Entidade de agendamento criada
        """
        # Verificar conflitos de horário
        if self.check_conflicts(
            provider_id=data['provider_id'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            subscriber_id=subscriber_id
        ):
            self.logger.error(
                f"Conflito de horário detectado para provider_id={data['provider_id']}, "
                f"start_time={data['start_time']}, end_time={data['end_time']}"
            )
            raise ValueError("Conflito de horário: Este profissional já possui um agendamento neste horário")
            
        # Criar agendamento
        appointment = Appointment(
            subscriber_id=subscriber_id,
            patient_id=data['patient_id'],
            provider_id=data['provider_id'],
            service_name=data['service_name'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            status=data.get('status', 'scheduled'),
            notes=data.get('notes')
        )
        
        try:
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            self.logger.info(f"Agendamento criado com sucesso: {appointment.id}")
            return self._model_to_entity(appointment)
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao criar agendamento: {str(e)}")
            raise
    
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Busca um agendamento pelo ID
        
        Args:
            id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AppointmentEntity]: Entidade de agendamento ou None se não encontrado
        """
        appointment = self.db.query(Appointment).filter(
            Appointment.id == id,
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        ).first()
        
        if appointment:
            return self._model_to_entity(appointment)
        
        return None
    
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
        appointment = self.db.query(Appointment).filter(
            Appointment.id == id,
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        ).first()
        
        if not appointment:
            self.logger.warning(f"Agendamento não encontrado para atualização: {id}")
            return None
        
        # Verificar conflitos de horário se datas estiverem sendo atualizadas
        if 'start_time' in data or 'end_time' in data:
            start_time = data.get('start_time', appointment.start_time)
            end_time = data.get('end_time', appointment.end_time)
            provider_id = data.get('provider_id', appointment.provider_id)
            
            if self.check_conflicts(
                provider_id=provider_id,
                start_time=start_time,
                end_time=end_time,
                subscriber_id=subscriber_id,
                exclude_id=id
            ):
                self.logger.error(
                    f"Conflito de horário detectado na atualização para provider_id={provider_id}, "
                    f"start_time={start_time}, end_time={end_time}"
                )
                raise ValueError("Conflito de horário: Este profissional já possui um agendamento neste horário")
                
        # Atualizar campos
        if 'patient_id' in data:
            appointment.patient_id = data['patient_id']
        if 'provider_id' in data:
            appointment.provider_id = data['provider_id']
        if 'service_name' in data:
            appointment.service_name = data['service_name']
        if 'start_time' in data:
            appointment.start_time = data['start_time']
        if 'end_time' in data:
            appointment.end_time = data['end_time']
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
            
        appointment.updated_at = datetime.now()
        
        try:
            self.db.commit()
            self.db.refresh(appointment)
            self.logger.info(f"Agendamento atualizado com sucesso: {id}")
            return self._model_to_entity(appointment)
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao atualizar agendamento: {str(e)}")
            raise
    
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Remove logicamente um agendamento (soft delete)
        
        Args:
            id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        appointment = self.db.query(Appointment).filter(
            Appointment.id == id,
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        ).first()
        
        if not appointment:
            self.logger.warning(f"Agendamento não encontrado para remoção: {id}")
            return False
        
        try:
            # Soft delete
            appointment.is_active = False
            appointment.status = "cancelled"
            appointment.updated_at = datetime.now()
            
            self.db.commit()
            self.logger.info(f"Agendamento removido com sucesso: {id}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao remover agendamento: {str(e)}")
            return False
    
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
        query = self.db.query(Appointment).filter(
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        )
        
        # Aplicar filtros
        if date_from:
            query = query.filter(Appointment.start_time >= date_from)
        
        if date_to:
            query = query.filter(Appointment.start_time <= date_to)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if provider_id:
            query = query.filter(Appointment.provider_id == provider_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        # Ordenar por data de início (mais recentes primeiro)
        query = query.order_by(desc(Appointment.start_time))
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        appointments = query.all()
        
        return [self._model_to_entity(appointment) for appointment in appointments]
    
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
        query = self.db.query(Appointment).filter(
            Appointment.provider_id == provider_id,
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True,
            Appointment.status.in_(["scheduled", "confirmed", "rescheduled"]),
            # Verificar se há sobreposição de horários
            or_(
                # Caso 1: O início do novo agendamento está entre o início e o fim de um agendamento existente
                and_(
                    Appointment.start_time <= start_time,
                    Appointment.end_time > start_time
                ),
                # Caso 2: O fim do novo agendamento está entre o início e o fim de um agendamento existente
                and_(
                    Appointment.start_time < end_time,
                    Appointment.end_time >= end_time
                ),
                # Caso 3: O novo agendamento engloba completamente um agendamento existente
                and_(
                    Appointment.start_time >= start_time,
                    Appointment.end_time <= end_time
                )
            )
        )
        
        # Excluir o próprio agendamento da verificação (para updates)
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
        
        # Se encontrar algum agendamento conflitante, retorna True
        return query.first() is not None