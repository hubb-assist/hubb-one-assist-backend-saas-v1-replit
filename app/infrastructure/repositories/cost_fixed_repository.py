from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.domain.cost_fixed.entities import CostFixedEntity
from app.domain.cost_fixed.interfaces import ICostFixedRepository
from app.db.models_cost_fixed import CostFixed


class CostFixedSQLAlchemyRepository(ICostFixedRepository):
    """Implementação SQLAlchemy do repositório de custos fixos."""

    def __init__(self, db: Session):
        self.db = db

    def _map_to_entity(self, model: CostFixed) -> CostFixedEntity:
        """Converte um modelo SQLAlchemy para uma entidade de domínio."""
        return CostFixedEntity(
            id=model.id,
            nome=model.nome,
            valor=model.valor,
            data=model.data,
            subscriber_id=model.subscriber_id,
            observacoes=model.observacoes,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def create(self, cost_fixed: CostFixedEntity) -> CostFixedEntity:
        """Cria um novo registro de custo fixo."""
        db_cost_fixed = CostFixed(
            id=cost_fixed.id,
            nome=cost_fixed.nome,
            valor=cost_fixed.valor,
            data=cost_fixed.data,
            subscriber_id=cost_fixed.subscriber_id,
            observacoes=cost_fixed.observacoes,
            is_active=cost_fixed.is_active,
            created_at=cost_fixed.created_at,
            updated_at=cost_fixed.updated_at
        )
        
        self.db.add(db_cost_fixed)
        self.db.commit()
        self.db.refresh(db_cost_fixed)
        
        return self._map_to_entity(db_cost_fixed)

    def get_by_id(self, cost_fixed_id: UUID, subscriber_id: UUID) -> Optional[CostFixedEntity]:
        """Obtém um custo fixo pelo seu ID."""
        db_cost_fixed = self.db.query(CostFixed).filter(
            CostFixed.id == cost_fixed_id,
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        ).first()
        
        if not db_cost_fixed:
            return None
            
        return self._map_to_entity(db_cost_fixed)

    def update(self, cost_fixed_id: UUID, cost_fixed_update: Dict[str, Any], subscriber_id: UUID) -> Optional[CostFixedEntity]:
        """Atualiza um custo fixo existente."""
        db_cost_fixed = self.db.query(CostFixed).filter(
            CostFixed.id == cost_fixed_id,
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        ).first()
        
        if not db_cost_fixed:
            return None
            
        # Atualiza os campos permitidos
        for key, value in cost_fixed_update.items():
            if hasattr(db_cost_fixed, key):
                setattr(db_cost_fixed, key, value)
        
        self.db.commit()
        self.db.refresh(db_cost_fixed)
        
        return self._map_to_entity(db_cost_fixed)

    def delete(self, cost_fixed_id: UUID, subscriber_id: UUID) -> bool:
        """Remove (desativa) um custo fixo."""
        db_cost_fixed = self.db.query(CostFixed).filter(
            CostFixed.id == cost_fixed_id,
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        ).first()
        
        if not db_cost_fixed:
            return False
            
        # Exclusão lógica (desativação)
        db_cost_fixed.is_active = False
        
        self.db.commit()
        
        return True

    def list_all(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> List[CostFixedEntity]:
        """Lista todos os custos fixos de um assinante, com opção de filtro por data."""
        query = self.db.query(CostFixed).filter(
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        )
        
        # Aplica filtros de data se fornecidos
        if date_from:
            query = query.filter(CostFixed.data >= date_from)
        
        if date_to:
            query = query.filter(CostFixed.data <= date_to)
        
        # Ordena por data decrescente (mais recente primeiro)
        query = query.order_by(desc(CostFixed.data))
        
        # Aplica paginação
        db_costs = query.offset(skip).limit(limit).all()
        
        # Converte para entidades de domínio
        return [self._map_to_entity(item) for item in db_costs]

    def count(
        self, 
        subscriber_id: UUID,
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> int:
        """Conta o número total de custos fixos de um assinante."""
        query = self.db.query(CostFixed).filter(
            CostFixed.subscriber_id == subscriber_id,
            CostFixed.is_active == True
        )
        
        # Aplica filtros de data se fornecidos
        if date_from:
            query = query.filter(CostFixed.data >= date_from)
        
        if date_to:
            query = query.filter(CostFixed.data <= date_to)
        
        return query.count()