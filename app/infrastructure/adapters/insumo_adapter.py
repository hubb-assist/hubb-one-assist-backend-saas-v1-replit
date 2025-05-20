"""
Adaptador para converter entre modelos de banco de dados e entidades de domínio para insumos.
"""
from typing import Optional, Dict, Any, List
from uuid import UUID

from app.db.models.insumo import Insumo
from app.domain.insumo.entities import InsumoEntity


class InsumoAdapter:
    """
    Adaptador para converter entre modelos de banco de dados e entidades de domínio para insumos.
    """
    
    @staticmethod
    def to_entity(model: Insumo) -> InsumoEntity:
        """
        Converte um modelo de banco de dados em uma entidade de domínio.
        
        Args:
            model: Modelo de banco de dados do insumo
            
        Returns:
            InsumoEntity: Entidade de domínio equivalente
        """
        if not model:
            return None
            
        return InsumoEntity(
            id=model.id,
            subscriber_id=model.subscriber_id,
            nome=model.nome,
            tipo=model.tipo,
            unidade=model.unidade,
            quantidade=model.quantidade,
            categoria=model.categoria,
            observacoes=model.observacoes,
            modulo_id=model.modulo_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(entity: InsumoEntity) -> Insumo:
        """
        Converte uma entidade de domínio em um modelo de banco de dados.
        
        Args:
            entity: Entidade de domínio do insumo
            
        Returns:
            Insumo: Modelo de banco de dados equivalente
        """
        if not entity:
            return None
            
        # Se já existe no banco, atualiza o modelo
        model = Insumo()
        
        if entity.id:
            model.id = entity.id
        
        model.subscriber_id = entity.subscriber_id
        model.nome = entity.nome
        model.tipo = entity.tipo
        model.unidade = entity.unidade
        model.quantidade = entity.quantidade
        model.categoria = entity.categoria
        model.modulo_id = entity.modulo_id
        model.observacoes = entity.observacoes
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        
        return model
    
    @staticmethod
    def to_entity_list(models: List[Insumo]) -> List[InsumoEntity]:
        """
        Converte uma lista de modelos em uma lista de entidades.
        
        Args:
            models: Lista de modelos de banco de dados
            
        Returns:
            List[InsumoEntity]: Lista de entidades de domínio
        """
        return [InsumoAdapter.to_entity(model) for model in models if model]