"""
Implementação SQLAlchemy do repositório de agendamentos
"""
from datetime import datetime
from typing import List, Optional
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
    
    def _entity_to_model(self, appointment: Appointment) -> AppointmentModel:
        """
        Converte uma entidade de domínio para um modelo SQLAlchemy
        
        Args:
            appointment: Entidade de domínio
            
        Returns:
            AppointmentModel: Modelo SQLAlchemy
        """
        return AppointmentModel(
            id=appointment.id,
            subscriber_id=appointment.subscriber_id,
            patient_id=appointment.patient_id,
            provider_id=appointment.provider_id,
            service_name=appointment.service_name,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
            notes=appointment.notes,
            is_active=appointment.is_active,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at
        )
    
    def _model_to_entity(self, model: AppointmentModel) -> Appointment:
        """
        Converte um modelo SQLAlchemy para uma entidade de domínio
        
        Args:
            model: Modelo SQLAlchemy
            
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
    
    def create(self, appointment: Appointment) -> Appointment:
        """
        Cria um novo agendamento no banco de dados
        
        Args:
            appointment: Entidade Appointment a ser criada
            
        Returns:
            Appointment: Entidade criada com ID gerado
            
        Raises:
            ValueError: Se houver erro na validação ou criação
        """
        try:
            model = self._entity_to_model(appointment)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)
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
            Appointment: Entidade encontrada
            
        Raises:
            ValueError: Se o agendamento não for encontrado
        """
        model = (
            self.db.query(AppointmentModel)
            .filter(
                and_(
                    AppointmentModel.id == appointment_id,
                    AppointmentModel.subscriber_id == subscriber_id,
                    AppointmentModel.is_active == True
                )
            )
            .first()
        )
        
        if not model:
            raise ValueError(f"Agendamento com ID {appointment_id} não encontrado")
        
        return self._model_to_entity(model)
    
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
        model = (
            self.db.query(AppointmentModel)
            .filter(
                and_(
                    AppointmentModel.id == appointment.id,
                    AppointmentModel.subscriber_id == appointment.subscriber_id,
                    AppointmentModel.is_active == True
                )
            )
            .first()
        )
        
        if not model:
            raise ValueError(f"Agendamento com ID {appointment.id} não encontrado")
        
        try:
            # Atualizar os atributos do modelo
            model.patient_id = appointment.patient_id
            model.provider_id = appointment.provider_id
            model.service_name = appointment.service_name
            model.start_time = appointment.start_time
            model.end_time = appointment.end_time
            model.status = appointment.status
            model.notes = appointment.notes
            model.updated_at = appointment.updated_at or datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)
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
        model = (
            self.db.query(AppointmentModel)
            .filter(
                and_(
                    AppointmentModel.id == appointment_id,
                    AppointmentModel.subscriber_id == subscriber_id,
                    AppointmentModel.is_active == True
                )
            )
            .first()
        )
        
        if not model:
            raise ValueError(f"Agendamento com ID {appointment_id} não encontrado")
        
        try:
            model.is_active = False
            model.updated_at = datetime.utcnow()
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
        provider_id: Optional[int] = None,
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
        # Construir a consulta base
        query = (
            self.db.query(AppointmentModel)
            .filter(
                and_(
                    AppointmentModel.subscriber_id == subscriber_id,
                    AppointmentModel.is_active == True
                )
            )
        )
        
        # Aplicar filtros opcionais
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
        
        # Ordenar, paginar e executar a consulta
        models = (
            query.order_by(AppointmentModel.start_time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        # Converter os modelos para entidades
        return [self._model_to_entity(model) for model in models]