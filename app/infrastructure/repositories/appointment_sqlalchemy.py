"""
Implementação SQLAlchemy do repositório de Agendamentos.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import and_, or_, between
from sqlalchemy.orm import Session

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository
from app.db.models_appointment import Appointment


class AppointmentRepository(IAppointmentRepository):
    """
    Implementação do repositório de Agendamentos usando SQLAlchemy.
    """
    
    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma sessão de banco de dados.
        
        Args:
            db: Sessão SQLAlchemy
        """
        self.db = db
    
    def create(self, appointment: AppointmentEntity) -> AppointmentEntity:
        """
        Cria um novo agendamento no banco de dados.
        
        Args:
            appointment: Entidade de agendamento a ser criada
            
        Returns:
            AppointmentEntity: Entidade criada com ID gerado
            
        Raises:
            ValueError: Se houver conflito de horário
        """
        # Verificar conflitos de horário antes de criar
        if self.check_conflicts(
            appointment.provider_id,
            appointment.start_time,
            appointment.end_time
        ):
            raise ValueError(
                f"Conflito de horário para o profissional {appointment.provider_id} "
                f"entre {appointment.start_time} e {appointment.end_time}"
            )
        
        # Criar modelo de banco de dados a partir da entidade
        db_appointment = Appointment(
            id=appointment.id,
            subscriber_id=appointment.subscriber_id,
            patient_id=appointment.patient_id,
            provider_id=appointment.provider_id,
            service_id=appointment.service_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
            notes=appointment.notes,
            is_active=appointment.is_active,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at
        )
        
        # Persistir no banco de dados
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        
        # Retornar entidade criada
        return self._to_entity(db_appointment)
    
    def get_by_id(self, appointment_id: UUID, subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Busca um agendamento por ID com isolamento por subscriber_id.
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante
            
        Returns:
            Optional[AppointmentEntity]: Entidade encontrada ou None se não existir
        """
        db_appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        ).first()
        
        if not db_appointment:
            return None
        
        return self._to_entity(db_appointment)
    
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
        # Buscar o agendamento atual
        db_appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment.id,
            Appointment.subscriber_id == appointment.subscriber_id,
            Appointment.is_active == True
        ).first()
        
        if not db_appointment:
            raise ValueError(f"Agendamento com ID {appointment.id} não encontrado")
        
        # Verificar conflitos de horário (apenas se houver mudança nos horários)
        if (db_appointment.start_time != appointment.start_time or 
            db_appointment.end_time != appointment.end_time):
            if self.check_conflicts(
                appointment.provider_id,
                appointment.start_time,
                appointment.end_time,
                appointment.id
            ):
                raise ValueError(
                    f"Conflito de horário para o profissional {appointment.provider_id} "
                    f"entre {appointment.start_time} e {appointment.end_time}"
                )
        
        # Atualizar os campos
        db_appointment.patient_id = appointment.patient_id
        db_appointment.provider_id = appointment.provider_id
        db_appointment.service_id = appointment.service_id
        db_appointment.start_time = appointment.start_time
        db_appointment.end_time = appointment.end_time
        db_appointment.status = appointment.status
        db_appointment.notes = appointment.notes
        db_appointment.updated_at = datetime.utcnow()
        
        # Persistir as alterações
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        
        return self._to_entity(db_appointment)
    
    def delete(self, appointment_id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui (desativa) um agendamento.
        
        Args:
            appointment_id: ID do agendamento a ser excluído
            subscriber_id: ID do assinante
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        db_appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        ).first()
        
        if not db_appointment:
            return False
        
        # Exclusão lógica (soft delete)
        db_appointment.is_active = False
        db_appointment.updated_at = datetime.utcnow()
        
        self.db.add(db_appointment)
        self.db.commit()
        
        return True
    
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
            subscriber_id: ID do assinante
            skip: Quantidade de registros para pular (paginação)
            limit: Quantidade máxima de registros para retornar
            filters: Filtros opcionais (patient_id, provider_id, status, date_from, date_to, etc.)
            
        Returns:
            List[AppointmentEntity]: Lista de entidades encontradas
        """
        filters = filters or {}
        query = self.db.query(Appointment).filter(
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        )
        
        # Aplicar filtros opcionais
        query = self._apply_filters(query, filters)
        
        # Aplicar paginação
        query = query.order_by(Appointment.start_time.desc()).offset(skip).limit(limit)
        
        # Executar a consulta
        db_appointments = query.all()
        
        # Converter para entidades
        return [self._to_entity(db_appointment) for db_appointment in db_appointments]
    
    def count(self, subscriber_id: UUID, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o total de agendamentos, aplicando filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante
            filters: Filtros opcionais (patient_id, provider_id, status, date_from, date_to, etc.)
            
        Returns:
            int: Número total de registros
        """
        filters = filters or {}
        query = self.db.query(Appointment).filter(
            Appointment.subscriber_id == subscriber_id,
            Appointment.is_active == True
        )
        
        # Aplicar filtros opcionais
        query = self._apply_filters(query, filters)
        
        # Contar registros
        return query.count()
    
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
        # Construir a consulta base
        query = self.db.query(Appointment).filter(
            Appointment.provider_id == provider_id,
            Appointment.is_active == True,
            Appointment.status.in_(["scheduled", "confirmed"])  # Apenas agendamentos ativos
        )
        
        # Ignorar o próprio agendamento em caso de atualização
        if appointment_id:
            query = query.filter(Appointment.id != appointment_id)
        
        # Verificar sobreposição de horários
        # Conflito ocorre quando:
        # 1. O início do novo está dentro de um existente: start_time está entre start e end de um existente
        # 2. O fim do novo está dentro de um existente: end_time está entre start e end de um existente
        # 3. O novo contém um existente: start_time <= start de existente e end_time >= end de existente
        conflicts = query.filter(
            or_(
                # Caso 1 e 2: o novo sobrepõe parcialmente um existente
                and_(
                    Appointment.start_time <= end_time,
                    Appointment.end_time >= start_time
                ),
                # Caso 3: o novo contém completamente um existente
                and_(
                    Appointment.start_time >= start_time,
                    Appointment.end_time <= end_time
                )
            )
        ).first()
        
        return conflicts is not None
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Aplica filtros à consulta base.
        
        Args:
            query: Consulta SQLAlchemy
            filters: Dicionário de filtros
            
        Returns:
            Query SQLAlchemy com filtros aplicados
        """
        if 'patient_id' in filters and filters['patient_id']:
            query = query.filter(Appointment.patient_id == filters['patient_id'])
        
        if 'provider_id' in filters and filters['provider_id']:
            query = query.filter(Appointment.provider_id == filters['provider_id'])
        
        if 'service_id' in filters and filters['service_id']:
            query = query.filter(Appointment.service_id == filters['service_id'])
        
        if 'status' in filters and filters['status']:
            query = query.filter(Appointment.status == filters['status'])
        
        if 'date_from' in filters and filters['date_from']:
            query = query.filter(Appointment.start_time >= filters['date_from'])
        
        if 'date_to' in filters and filters['date_to']:
            query = query.filter(Appointment.start_time <= filters['date_to'])
        
        return query
    
    def _to_entity(self, db_appointment: Appointment) -> AppointmentEntity:
        """
        Converte um modelo de banco de dados em uma entidade de domínio.
        
        Args:
            db_appointment: Modelo SQLAlchemy
            
        Returns:
            AppointmentEntity: Entidade de domínio
        """
        return AppointmentEntity(
            id=db_appointment.id,
            subscriber_id=db_appointment.subscriber_id,
            patient_id=db_appointment.patient_id,
            provider_id=db_appointment.provider_id,
            service_id=db_appointment.service_id,
            start_time=db_appointment.start_time,
            end_time=db_appointment.end_time,
            status=db_appointment.status,
            notes=db_appointment.notes,
            is_active=db_appointment.is_active,
            created_at=db_appointment.created_at,
            updated_at=db_appointment.updated_at
        )