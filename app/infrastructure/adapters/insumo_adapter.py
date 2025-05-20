"""
Adaptador para converter entre modelo SQLAlchemy e entidade de domínio de Insumo.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.db.models import Insumo, InsumoModuleAssociation, Module
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class InsumoAdapter:
    """
    Adaptador para converter entre o modelo SQLAlchemy Insumo e a entidade InsumoEntity.
    
    Esta classe é responsável por mapear os dados entre o modelo de banco de dados e a entidade de domínio,
    garantindo que a lógica de domínio permaneça limpa e independente da implementação de persistência.
    """
    
    @staticmethod
    def to_entity(insumo_model: Insumo) -> InsumoEntity:
        """
        Converte modelo SQLAlchemy para entidade de domínio.
        
        Args:
            insumo_model: Modelo SQLAlchemy de Insumo
            
        Returns:
            InsumoEntity: Entidade de domínio correspondente
        """
        # Converter associações com módulos para value objects
        modules_used = []
        if insumo_model.modules_used:
            for association in insumo_model.modules_used:
                module_nome = association.module.nome if association.module else None
                modules_used.append(ModuloAssociation(
                    module_id=association.module_id,
                    quantidade_padrao=association.quantidade_padrao,
                    observacao=association.observacao,
                    module_nome=module_nome,
                    created_at=association.created_at,
                    updated_at=association.updated_at
                ))
        
        # Converter o modelo para entidade
        return InsumoEntity(
            id=insumo_model.id,
            nome=insumo_model.nome,
            descricao=insumo_model.descricao,
            categoria=insumo_model.categoria,
            valor_unitario=float(insumo_model.valor_unitario),  # Converter de Decimal para float
            unidade_medida=insumo_model.unidade_medida,
            estoque_minimo=insumo_model.estoque_minimo,
            estoque_atual=insumo_model.estoque_atual,
            subscriber_id=insumo_model.subscriber_id,
            fornecedor=insumo_model.fornecedor,
            codigo_referencia=insumo_model.codigo_referencia,
            data_validade=insumo_model.data_validade,
            data_compra=insumo_model.data_compra,
            observacoes=insumo_model.observacoes,
            is_active=insumo_model.is_active,
            created_at=insumo_model.created_at,
            updated_at=insumo_model.updated_at,
            modules_used=modules_used
        )
    
    @staticmethod
    def to_model(insumo_entity: InsumoEntity, insumo_model: Optional[Insumo] = None) -> Insumo:
        """
        Converte entidade de domínio para modelo SQLAlchemy.
        
        Args:
            insumo_entity: Entidade de domínio InsumoEntity
            insumo_model: Modelo SQLAlchemy existente a ser atualizado (opcional)
            
        Returns:
            Insumo: Modelo SQLAlchemy correspondente
        """
        # Se não foi fornecido um modelo existente, criar um novo
        if insumo_model is None:
            insumo_model = Insumo()
        
        # Atualizar campos do modelo com dados da entidade
        insumo_model.nome = insumo_entity.nome
        insumo_model.descricao = insumo_entity.descricao
        insumo_model.categoria = insumo_entity.categoria
        insumo_model.valor_unitario = insumo_entity.valor_unitario
        insumo_model.unidade_medida = insumo_entity.unidade_medida
        insumo_model.estoque_minimo = insumo_entity.estoque_minimo
        insumo_model.estoque_atual = insumo_entity.estoque_atual
        insumo_model.fornecedor = insumo_entity.fornecedor
        insumo_model.codigo_referencia = insumo_entity.codigo_referencia
        insumo_model.data_validade = insumo_entity.data_validade
        insumo_model.data_compra = insumo_entity.data_compra
        insumo_model.observacoes = insumo_entity.observacoes
        insumo_model.is_active = insumo_entity.is_active
        insumo_model.updated_at = datetime.utcnow()
        
        # Se a entidade tem ID e o modelo não, definir o ID do modelo
        if insumo_entity.id and not insumo_model.id:
            insumo_model.id = insumo_entity.id
            
        # Se a entidade tem subscriber_id e o modelo não, definir o subscriber_id do modelo
        if insumo_entity.subscriber_id and not insumo_model.subscriber_id:
            insumo_model.subscriber_id = insumo_entity.subscriber_id
        
        return insumo_model
    
    @staticmethod
    def map_module_associations(
        insumo_id: UUID, 
        modules_data: List[Dict[str, Any]], 
        session
    ) -> List[InsumoModuleAssociation]:
        """
        Mapeia dados de associações de módulos para modelos SQLAlchemy.
        
        Args:
            insumo_id: UUID do insumo
            modules_data: Lista de dicionários com dados de módulos
            session: Sessão SQLAlchemy para consultar módulos
            
        Returns:
            List[InsumoModuleAssociation]: Lista de modelos de associação
        """
        associations = []
        
        for module_data in modules_data:
            module_id = module_data.get("module_id")
            if not module_id:
                continue
                
            # Verificar se o módulo existe
            module = session.query(Module).filter(Module.id == module_id).first()
            if not module:
                continue
                
            # Criar associação
            association = InsumoModuleAssociation(
                insumo_id=insumo_id,
                module_id=module_id,
                quantidade_padrao=module_data.get("quantidade_padrao", 1),
                observacao=module_data.get("observacao")
            )
            
            associations.append(association)
            
        return associations