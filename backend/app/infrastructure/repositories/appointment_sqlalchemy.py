"""
Implementação SQLAlchemy do repositório de agendamentos
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.db.models_appointment import Appointment as AppointmentModel
from app.domain.appointment.entities import Appointment
from app.domain.appointment.interfaces import IAppointmentRepository


class AppointmentSQLAlchemyRepository(IAppointmentRepository):
    """
    Implementação do repositório de agendamentos usando SQLAlchemy
    """
    
    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma sessão do banco de dados
        
        Args:
            db: Sessão do SQLAlchemy
        """
        self.db = db
    
    def _to_entity(self, model: AppointmentModel) -> Appointment:
        """
        Converte o modelo SQLAlchemy para a entidade de domínio
        
        Args:
            model: Modelo do SQLAlchemy
            
        Returns:
            Appointment: Entidade de domínio
        """
        return Appointment(
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
    
    def _to_model(self, entity: Appointment) -> Dict[str, Any]:
        """
        Converte a entidade de domínio para um dicionário de atributos do modelo
        
        Args:
            entity: Entidade de domínio
            
        Returns:
            Dict[str, Any]: Dicionário com os atributos para o modelo SQLAlchemy
        """
        return {
            "id": entity.id,
            "subscriber_id": entity.subscriber_id,
            "patient_id": entity.patient_id,
            "provider_id": entity.provider_id,
            "service_name": entity.service_name,
            "start_time": entity.start_time,
            "end_time": entity.end_time,
            "status": entity.status,
            "notes": entity.notes,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at
        }
    
    def create(self, appointment: Appointment) -> Appointment:
        """
        Cria um novo agendamento no banco de dados
        
        Args:
            appointment: Entidade Appointment a ser criada
            
        Returns:
            Appointment: Entidade Appointment com ID gerado
            
        Raises:
            ValueError: Se houver erro na validação ou criação
        """
        try:
            model_data = self._to_model(appointment)
            appointment_model = AppointmentModel(**model_data)
            
            self.db.add(appointment_model)
            self.db.commit()
            self.db.refresh(appointment_model)
            
            return self._to_entity(appointment_model)
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao criar agendamento: {str(e)}")
    
    def get_by_id(self, appointment_id: UUID, subscriber_id: UUID) -> Appointment:
        """
        Busca um agendamento pelo ID
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante para segurança multi-tenant
            
        Returns:
            Appointment: Entidade Appointment encontrada
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        appointment_model = self.db.query(AppointmentModel).filter(
            AppointmentModel.id == appointment_id,
            AppointmentModel.subscriber_id == subscriber_id,
            AppointmentModel.is_active == True
        ).first()
        
        if not appointment_model:
            raise ValueError(f"Agendamento com ID {appointment_id} não encontrado")
        
        return self._to_entity(appointment_model)
    
    def update(self, appointment: Appointment) -> Appointment:
        """
        Atualiza um agendamento existente
        
        Args:
            appointment: Entidade Appointment com as atualizações
            
        Returns:
            Appointment: Entidade Appointment atualizada
            
        Raises:
            ValueError: Se o agendamento não for encontrado ou houver erro na validação
        """
        try:
            appointment_model = self.db.query(AppointmentModel).filter(
                AppointmentModel.id == appointment.id,
                AppointmentModel.subscriber_id == appointment.subscriber_id,
                AppointmentModel.is_active == True
            ).first()
            
            if not appointment_model:
                raise ValueError(f"Agendamento com ID {appointment.id} não encontrado")
            
            model_data = self._to_model(appointment)
            
            for key, value in model_data.items():
                setattr(appointment_model, key, value)
            
            self.db.commit()
            self.db.refresh(appointment_model)
            
            return self._to_entity(appointment_model)
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao atualizar agendamento: {str(e)}")
    
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
        try:
            appointment_model = self.db.query(AppointmentModel).filter(
                AppointmentModel.id == appointment_id,
                AppointmentModel.subscriber_id == subscriber_id,
                AppointmentModel.is_active == True
            ).first()
            
            if not appointment_model:
                raise ValueError(f"Agendamento com ID {appointment_id} não encontrado")
            
            appointment_model.is_active = False
            appointment_model.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Erro ao excluir agendamento: {str(e)}")
    
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
        query = self.db.query(AppointmentModel).filter(
            AppointmentModel.subscriber_id == subscriber_id,
            AppointmentModel.is_active == True
        )
        
        # Aplicar filtros adicionais se fornecidos
        if date_from:
            query = query.filter(AppointmentModel.start_time >= date_from)
        
        if date_to:
            query = query.filter(AppointmentModel.start_time <= date_to)
        
        if patient_id:
            query = query.filter(AppointmentModel.patient_id == patient_id)
        
        if provider_id:
            query = query.filter(AppointmentModel.provider_id == provider_id)
        
        if status:
            query = query.filter(AppointmentModel.status == status)
        
        # Ordenar por data/hora de início
        query = query.order_by(AppointmentModel.start_time)
        
        # Aplicar paginação
        appointments_models = query.offset(skip).limit(limit).all()
        
        # Converter para entidades de domínio
        return [self._to_entity(model) for model in appointments_models]