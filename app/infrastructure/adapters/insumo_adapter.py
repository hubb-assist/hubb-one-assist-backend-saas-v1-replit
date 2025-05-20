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
        if model is None:
            raise ValueError("Modelo não pode ser None")
        
        # Extrair valores do modelo para variáveis regulares para evitar problemas de tipagem
        id_val = model.id
        subscriber_id_val = model.subscriber_id
        nome_val = model.nome
        tipo_val = model.tipo
        unidade_val = model.unidade
        quantidade_val = model.quantidade
        categoria_val = model.categoria
        observacoes_val = model.observacoes
        modulo_id_val = model.modulo_id
        is_active_val = model.is_active
        created_at_val = model.created_at
        updated_at_val = model.updated_at
        
        # Converter para os tipos esperados pela entidade
        subscriber_id_converted = UUID(str(subscriber_id_val)) if subscriber_id_val else None
        modulo_id_converted = UUID(str(modulo_id_val)) if modulo_id_val else None
        
        return InsumoEntity(
            id=id_val,
            subscriber_id=subscriber_id_converted,
            nome=str(nome_val),
            tipo=str(tipo_val),
            unidade=str(unidade_val),
            quantidade=float(quantidade_val) if quantidade_val is not None else 0.0,
            categoria=str(categoria_val),
            observacoes=str(observacoes_val) if observacoes_val else None,
            modulo_id=modulo_id_converted,
            is_active=bool(is_active_val),
            created_at=created_at_val,
            updated_at=updated_at_val
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
            raise ValueError("Entidade não pode ser None")
            
        # Se já existe no banco, atualiza o modelo
        model = Insumo()
        
        if entity.id:
            model.id = entity.id
        
        # Atribuir valores com setattr para evitar problemas de tipagem
        setattr(model, 'subscriber_id', entity.subscriber_id)
        setattr(model, 'nome', entity.nome)
        setattr(model, 'tipo', entity.tipo)
        setattr(model, 'unidade', entity.unidade)
        setattr(model, 'quantidade', entity.quantidade)
        setattr(model, 'categoria', entity.categoria)
        setattr(model, 'modulo_id', entity.modulo_id)
        setattr(model, 'observacoes', entity.observacoes)
        setattr(model, 'is_active', entity.is_active)
        setattr(model, 'updated_at', entity.updated_at)
        
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