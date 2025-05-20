"""
Adaptador para converter entre entidades de domínio e modelos de banco de dados para Insumos.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.db.models.insumo import Insumo
from app.domain.insumo.entities import InsumoEntity


class InsumoAdapter:
    """
    Adaptador para converter entre entidades de domínio e modelos ORM para Insumos.
    """
    
    @staticmethod
    def to_entity(insumo_orm: Insumo) -> InsumoEntity:
        """
        Converte um modelo ORM de insumo para uma entidade de domínio.
        
        Args:
            insumo_orm: Modelo ORM de insumo
            
        Returns:
            InsumoEntity: Entidade de domínio de insumo
        """
        # Extrai os IDs dos módulos relacionados
        modules_used = [module.id for module in insumo_orm.modules] if insumo_orm.modules else []
        
        return InsumoEntity(
            id=insumo_orm.id,
            nome=insumo_orm.nome,
            descricao=insumo_orm.descricao,
            categoria=insumo_orm.categoria,
            valor_unitario=Decimal(str(insumo_orm.valor_unitario)),
            unidade_medida=insumo_orm.unidade_medida,
            estoque_minimo=insumo_orm.estoque_minimo,
            estoque_atual=insumo_orm.estoque_atual,
            subscriber_id=insumo_orm.subscriber_id,
            fornecedor=insumo_orm.fornecedor,
            codigo_referencia=insumo_orm.codigo_referencia,
            data_validade=insumo_orm.data_validade,
            data_compra=insumo_orm.data_compra,
            observacoes=insumo_orm.observacoes,
            is_active=insumo_orm.is_active,
            created_at=insumo_orm.created_at,
            updated_at=insumo_orm.updated_at,
            modules_used=modules_used
        )
    
    @staticmethod
    def to_orm(insumo_entity: InsumoEntity) -> Insumo:
        """
        Converte uma entidade de domínio de insumo para um modelo ORM.
        
        Args:
            insumo_entity: Entidade de domínio de insumo
            
        Returns:
            Insumo: Modelo ORM de insumo
        """
        # Cria um novo modelo ORM mas não define os relacionamentos aqui
        # Os relacionamentos serão tratados no repositório
        return Insumo(
            id=insumo_entity.id,
            nome=insumo_entity.nome,
            descricao=insumo_entity.descricao,
            categoria=insumo_entity.categoria,
            valor_unitario=float(insumo_entity.valor_unitario),
            unidade_medida=insumo_entity.unidade_medida,
            estoque_minimo=insumo_entity.estoque_minimo,
            estoque_atual=insumo_entity.estoque_atual,
            subscriber_id=insumo_entity.subscriber_id,
            fornecedor=insumo_entity.fornecedor,
            codigo_referencia=insumo_entity.codigo_referencia,
            data_validade=insumo_entity.data_validade,
            data_compra=insumo_entity.data_compra,
            observacoes=insumo_entity.observacoes,
            is_active=insumo_entity.is_active,
            created_at=insumo_entity.created_at,
            updated_at=insumo_entity.updated_at
        )
    
    @staticmethod
    def update_orm_from_entity(insumo_orm: Insumo, insumo_entity: InsumoEntity) -> Insumo:
        """
        Atualiza um modelo ORM com os valores de uma entidade de domínio.
        
        Args:
            insumo_orm: Modelo ORM a ser atualizado
            insumo_entity: Entidade de domínio com novos valores
            
        Returns:
            Insumo: Modelo ORM atualizado
        """
        insumo_orm.nome = insumo_entity.nome
        insumo_orm.descricao = insumo_entity.descricao
        insumo_orm.categoria = insumo_entity.categoria
        insumo_orm.valor_unitario = float(insumo_entity.valor_unitario)
        insumo_orm.unidade_medida = insumo_entity.unidade_medida
        insumo_orm.estoque_minimo = insumo_entity.estoque_minimo
        insumo_orm.estoque_atual = insumo_entity.estoque_atual
        insumo_orm.fornecedor = insumo_entity.fornecedor
        insumo_orm.codigo_referencia = insumo_entity.codigo_referencia
        insumo_orm.data_validade = insumo_entity.data_validade
        insumo_orm.data_compra = insumo_entity.data_compra
        insumo_orm.observacoes = insumo_entity.observacoes
        insumo_orm.is_active = insumo_entity.is_active
        insumo_orm.updated_at = datetime.utcnow()
        
        # Os relacionamentos devem ser tratados separadamente no repositório
        return insumo_orm
    
    @staticmethod
    def update_orm_from_dict(insumo_orm: Insumo, data: Dict[str, Any]) -> Insumo:
        """
        Atualiza um modelo ORM com os valores de um dicionário.
        
        Args:
            insumo_orm: Modelo ORM a ser atualizado
            data: Dicionário com os novos valores
            
        Returns:
            Insumo: Modelo ORM atualizado
        """
        # Atualiza apenas os campos presentes no dicionário
        for key, value in data.items():
            if key == 'valor_unitario' and value is not None:
                # Converte decimal para float para o ORM
                setattr(insumo_orm, key, float(value))
            elif hasattr(insumo_orm, key) and key != 'id' and key != 'subscriber_id':
                setattr(insumo_orm, key, value)
        
        # Sempre atualiza o timestamp
        insumo_orm.updated_at = datetime.utcnow()
        
        return insumo_orm