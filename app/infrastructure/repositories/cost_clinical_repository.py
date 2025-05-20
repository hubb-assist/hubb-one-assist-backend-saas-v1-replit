from uuid import UUID
from datetime import date
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.domain.cost_clinical.interfaces import ICostClinicalRepository
from app.domain.cost_clinical.entities import CostClinicalEntity
from app.schemas.custo_clinico import CustoClinicalCreate, CustoClinicalUpdate
from app.db.models_cost_clinical import CostClinical

class CostClinicalSQLAlchemyRepository(ICostClinicalRepository):
    """
    Implementação do repositório de custos clínicos usando SQLAlchemy.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: CustoClinicalCreate, subscriber_id: UUID) -> CostClinicalEntity:
        """
        Cria um novo custo clínico.
        
        Args:
            data: Dados do custo clínico a ser criado
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico criado
        """
        # Calcular o custo total
        total_cost = data.duration_hours * data.hourly_rate
        
        # Criar o modelo do BD
        db_cost = CostClinical(
            subscriber_id=subscriber_id,
            procedure_name=data.procedure_name,
            duration_hours=data.duration_hours,
            hourly_rate=data.hourly_rate,
            total_cost=total_cost,
            date=data.date,
            observacoes=data.observacoes
        )
        
        # Persistir no BD
        self.db.add(db_cost)
        self.db.commit()
        self.db.refresh(db_cost)
        
        # Converter para entidade
        return self._to_entity(db_cost)
    
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[CostClinicalEntity]:
        """
        Obtém um custo clínico pelo ID.
        
        Args:
            id: ID do custo clínico
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico ou None se não encontrado
        """
        db_cost = self.db.query(CostClinical).filter(
            CostClinical.id == id,
            CostClinical.subscriber_id == subscriber_id,
            CostClinical.is_active == True
        ).first()
        
        if not db_cost:
            return None
        
        return self._to_entity(db_cost)
    
    def update(self, id: UUID, data: CustoClinicalUpdate, subscriber_id: UUID) -> Optional[CostClinicalEntity]:
        """
        Atualiza um custo clínico existente.
        
        Args:
            id: ID do custo clínico a ser atualizado
            data: Dados para atualização
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico atualizada ou None se não encontrado
        """
        db_cost = self.db.query(CostClinical).filter(
            CostClinical.id == id,
            CostClinical.subscriber_id == subscriber_id,
            CostClinical.is_active == True
        ).first()
        
        if not db_cost:
            return None
        
        # Converter para dicionário e remover valores None
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        
        # Se duração ou valor hora mudar, recalcular o custo total
        if "duration_hours" in update_data or "hourly_rate" in update_data:
            duration = update_data.get("duration_hours", db_cost.duration_hours)
            hourly_rate = update_data.get("hourly_rate", db_cost.hourly_rate)
            update_data["total_cost"] = Decimal(duration) * Decimal(hourly_rate)
        
        # Atualizar os campos
        for key, value in update_data.items():
            setattr(db_cost, key, value)
        
        # Persistir no BD
        self.db.commit()
        self.db.refresh(db_cost)
        
        return self._to_entity(db_cost)
    
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Remove logicamente um custo clínico.
        
        Args:
            id: ID do custo clínico a ser removido
            subscriber_id: ID do assinante
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        db_cost = self.db.query(CostClinical).filter(
            CostClinical.id == id,
            CostClinical.subscriber_id == subscriber_id,
            CostClinical.is_active == True
        ).first()
        
        if not db_cost:
            return False
        
        # Remover logicamente
        db_cost.is_active = False
        
        # Persistir no BD
        self.db.commit()
        
        return True
    
    def list_all(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[CostClinicalEntity]:
        """
        Lista todos os custos clínicos do assinante com paginação e filtragem por data.
        
        Args:
            subscriber_id: ID do assinante
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Lista de entidades de custos clínicos
        """
        # Consulta base
        query = self.db.query(CostClinical).filter(
            CostClinical.subscriber_id == subscriber_id,
            CostClinical.is_active == True
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            query = query.filter(CostClinical.date >= date_from)
            
        if date_to:
            query = query.filter(CostClinical.date <= date_to)
        
        # Ordenar e aplicar paginação
        db_costs = query.order_by(desc(CostClinical.date)).offset(skip).limit(limit).all()
        
        # Converter para entidades
        return [self._to_entity(cost) for cost in db_costs]
    
    def count(
        self,
        subscriber_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> int:
        """
        Conta o número total de custos clínicos do assinante.
        
        Args:
            subscriber_id: ID do assinante
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Número total de custos clínicos
        """
        # Consulta base
        query = self.db.query(CostClinical).filter(
            CostClinical.subscriber_id == subscriber_id,
            CostClinical.is_active == True
        )
        
        # Aplicar filtros de data se fornecidos
        if date_from:
            query = query.filter(CostClinical.date >= date_from)
            
        if date_to:
            query = query.filter(CostClinical.date <= date_to)
        
        return query.count()
    
    def _to_entity(self, db_cost: CostClinical) -> CostClinicalEntity:
        """
        Converte um modelo do BD para uma entidade de domínio.
        
        Args:
            db_cost: Modelo do BD
            
        Returns:
            Entidade de domínio
        """
        return CostClinicalEntity(
            id=db_cost.id,
            subscriber_id=db_cost.subscriber_id,
            procedure_name=db_cost.procedure_name,
            duration_hours=db_cost.duration_hours,
            hourly_rate=db_cost.hourly_rate,
            total_cost=db_cost.total_cost,
            date=db_cost.date,
            observacoes=db_cost.observacoes,
            is_active=db_cost.is_active,
            created_at=db_cost.created_at,
            updated_at=db_cost.updated_at
        )