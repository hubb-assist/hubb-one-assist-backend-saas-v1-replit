"""
Adaptador para converter entre entidades de domínio e modelos ORM para Insumos.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.insumo.entities import InsumoEntity
from app.db.models.insumo import Insumo


class InsumoAdapter:
    """
    Adaptador para converter entre entidades de domínio e modelos ORM para Insumos.
    """
    
    @staticmethod
    def to_entity(orm_model: Optional[Insumo]) -> Optional[InsumoEntity]:
        """
        Converte um modelo ORM para uma entidade de domínio.
        
        Args:
            orm_model: Modelo ORM a ser convertido
            
        Returns:
            Optional[InsumoEntity]: Entidade de domínio resultante, None se o modelo for None
        """
        if orm_model is None:
            return None
        
        return InsumoEntity(
            id=orm_model.id,
            subscriber_id=orm_model.subscriber_id,
            nome=orm_model.nome,
            tipo=orm_model.tipo,
            unidade=orm_model.unidade,
            quantidade=orm_model.quantidade,
            observacoes=orm_model.observacoes,
            categoria=orm_model.categoria,
            modulo_id=orm_model.modulo_id,
            is_active=orm_model.is_active,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at
        )
    
    @staticmethod
    def to_orm_model(entity: InsumoEntity) -> Insumo:
        """
        Converte uma entidade de domínio para um modelo ORM.
        
        Args:
            entity: Entidade de domínio a ser convertida
            
        Returns:
            Insumo: Modelo ORM resultante
        """
        orm_model = Insumo(
            id=entity.id,
            subscriber_id=entity.subscriber_id,
            nome=entity.nome,
            tipo=entity.tipo,
            unidade=entity.unidade,
            quantidade=entity.quantidade,
            observacoes=entity.observacoes,
            categoria=entity.categoria,
            modulo_id=entity.modulo_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        
        return orm_model
    
    @staticmethod
    def update_orm_model(orm_model: Insumo, entity: InsumoEntity) -> Insumo:
        """
        Atualiza um modelo ORM com os dados de uma entidade de domínio.
        
        Args:
            orm_model: Modelo ORM a ser atualizado
            entity: Entidade de domínio com os novos dados
            
        Returns:
            Insumo: Modelo ORM atualizado
        """
        orm_model.nome = entity.nome
        orm_model.tipo = entity.tipo
        orm_model.unidade = entity.unidade
        orm_model.quantidade = entity.quantidade
        orm_model.categoria = entity.categoria
        orm_model.modulo_id = entity.modulo_id
        orm_model.observacoes = entity.observacoes
        orm_model.is_active = entity.is_active
        orm_model.updated_at = datetime.utcnow()
        
        return orm_model