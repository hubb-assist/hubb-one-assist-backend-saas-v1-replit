"""
Adaptador para converter entre modelos de banco de dados e entidades de domínio para Insumos.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models_insumo import Insumo, InsumoModuleAssociation
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class InsumoAdapter:
    """
    Adaptador para converter entre modelos de banco de dados e entidades de domínio para Insumos.
    
    Esta classe segue o padrão Adapter, permitindo a compatibilidade entre
    diferentes interfaces (modelo de banco de dados e entidade de domínio).
    """
    
    @staticmethod
    def to_entity(model: Insumo) -> InsumoEntity:
        """
        Converte um modelo de banco de dados em uma entidade de domínio.
        
        Args:
            model: Modelo de banco de dados Insumo
            
        Returns:
            InsumoEntity: Entidade de domínio correspondente
        """
        # Converter associações com módulos
        module_associations = []
        
        if model.modules_used:
            for assoc in model.modules_used:
                module_associations.append(ModuloAssociation(
                    module_id=assoc.module_id,
                    quantidade_padrao=assoc.quantidade_padrao,
                    observacao=assoc.observacao,
                    # Como não temos acesso direto ao nome do módulo no modelo,
                    # o nome seria obtido de uma consulta ao módulo correspondente
                    module_nome=None
                ))
        
        # Formatar datas que podem vir como string
        data_validade = None
        if model.data_validade:
            if isinstance(model.data_validade, str):
                data_validade = datetime.fromisoformat(model.data_validade)
            else:
                data_validade = model.data_validade
                
        data_compra = None
        if model.data_compra:
            if isinstance(model.data_compra, str):
                data_compra = datetime.fromisoformat(model.data_compra)
            else:
                data_compra = model.data_compra
        
        # Criar e retornar a entidade
        return InsumoEntity(
            id=model.id,
            nome=model.nome,
            descricao=model.descricao,
            categoria=model.categoria,
            valor_unitario=model.valor_unitario,
            unidade_medida=model.unidade_medida,
            estoque_minimo=model.estoque_minimo,
            estoque_atual=model.estoque_atual,
            subscriber_id=model.subscriber_id,
            fornecedor=model.fornecedor,
            codigo_referencia=model.codigo_referencia,
            data_validade=data_validade,
            data_compra=data_compra,
            observacoes=model.observacoes,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            modules_used=module_associations
        )
    
    @staticmethod
    def to_model(entity: InsumoEntity) -> Insumo:
        """
        Converte uma entidade de domínio em um modelo de banco de dados.
        
        Args:
            entity: Entidade de domínio InsumoEntity
            
        Returns:
            Insumo: Modelo de banco de dados correspondente
        """
        # Criar modelo básico
        model = Insumo(
            id=entity.id,
            nome=entity.nome,
            descricao=entity.descricao,
            categoria=entity.categoria,
            valor_unitario=entity.valor_unitario,
            unidade_medida=entity.unidade_medida,
            estoque_minimo=entity.estoque_minimo,
            estoque_atual=entity.estoque_atual,
            subscriber_id=entity.subscriber_id,
            fornecedor=entity.fornecedor,
            codigo_referencia=entity.codigo_referencia,
            data_validade=entity.data_validade,
            data_compra=entity.data_compra,
            observacoes=entity.observacoes,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        
        # Criar associações com módulos
        if entity.modules_used:
            model.modules_used = []
            
            for assoc in entity.modules_used:
                model.modules_used.append(InsumoModuleAssociation(
                    insumo_id=entity.id,
                    module_id=assoc.module_id,
                    quantidade_padrao=assoc.quantidade_padrao,
                    observacao=assoc.observacao
                ))
        
        return model
    
    @staticmethod
    def update_model_from_entity(model: Insumo, entity: InsumoEntity, update_modules: bool = False) -> Insumo:
        """
        Atualiza um modelo existente com dados de uma entidade.
        
        Args:
            model: Modelo de banco de dados a ser atualizado
            entity: Entidade de domínio com os dados atualizados
            update_modules: Se True, atualiza também as associações com módulos
            
        Returns:
            Insumo: Modelo atualizado
        """
        # Atualizar campos básicos
        model.nome = entity.nome
        model.descricao = entity.descricao
        model.categoria = entity.categoria
        model.valor_unitario = entity.valor_unitario
        model.unidade_medida = entity.unidade_medida
        model.estoque_minimo = entity.estoque_minimo
        model.estoque_atual = entity.estoque_atual
        model.fornecedor = entity.fornecedor
        model.codigo_referencia = entity.codigo_referencia
        model.observacoes = entity.observacoes
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        
        # Atualizar datas
        if entity.data_validade is not None:
            model.data_validade = entity.data_validade
        else:
            model.data_validade = None
            
        if entity.data_compra is not None:
            model.data_compra = entity.data_compra
        else:
            model.data_compra = None
        
        # Atualizar associações com módulos, se solicitado
        if update_modules and entity.modules_used is not None:
            # Remover associações existentes
            model.modules_used = []
            
            # Adicionar novas associações
            for assoc in entity.modules_used:
                model.modules_used.append(InsumoModuleAssociation(
                    insumo_id=model.id,
                    module_id=assoc.module_id,
                    quantidade_padrao=assoc.quantidade_padrao,
                    observacao=assoc.observacao
                ))
        
        return model
    
    @staticmethod
    def apply_filters(query, filters: Dict[str, Any]) -> Any:
        """
        Aplica filtros a uma consulta SQLAlchemy.
        
        Args:
            query: Consulta SQLAlchemy base
            filters: Dicionário de filtros a serem aplicados
            
        Returns:
            Any: Consulta SQLAlchemy com filtros aplicados
        """
        if not filters:
            return query
            
        # Filtro por nome (busca parcial)
        if "nome" in filters and filters["nome"]:
            query = query.filter(Insumo.nome.ilike(f"%{filters['nome']}%"))
            
        # Filtro por categoria (busca exata)
        if "categoria" in filters and filters["categoria"]:
            query = query.filter(Insumo.categoria == filters["categoria"])
            
        # Filtro por fornecedor (busca parcial)
        if "fornecedor" in filters and filters["fornecedor"]:
            query = query.filter(Insumo.fornecedor.ilike(f"%{filters['fornecedor']}%"))
            
        # Filtro por estoque baixo
        if "estoque_baixo" in filters and filters["estoque_baixo"] is not None:
            if filters["estoque_baixo"]:
                query = query.filter(Insumo.estoque_atual < Insumo.estoque_minimo)
            
        # Filtro por módulo associado
        if "module_id" in filters and filters["module_id"]:
            module_id = filters["module_id"]
            query = query.join(InsumoModuleAssociation).filter(
                InsumoModuleAssociation.module_id == module_id
            )
            
        return query