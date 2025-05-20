"""
Adaptador para converter entre modelos de banco de dados e entidades do domínio para insumos.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from app.db.models.insumo import Insumo, InsumoModuleAssociation
from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.value_objects.modulo_association import ModuloAssociation


class InsumoAdapter:
    """
    Adaptador para converter entre modelos SQLAlchemy e entidades de domínio para insumos.
    
    Responsável por transformar entidades de domínio em modelos de banco de dados e vice-versa,
    mantendo a separação entre camadas conforme os princípios de Clean Architecture.
    """
    
    @staticmethod
    def to_entity(insumo_model: Insumo) -> InsumoEntity:
        """
        Converte um modelo de banco de dados em uma entidade de domínio.
        
        Args:
            insumo_model: Modelo SQLAlchemy de insumo
            
        Returns:
            InsumoEntity: Entidade de domínio correspondente
        """
        # Converter associações de módulos, se existirem
        modules_used = []
        if insumo_model.modules_used:
            for assoc in insumo_model.modules_used:
                module_nome = None
                if hasattr(assoc, 'module') and assoc.module:
                    module_nome = assoc.module.nome if hasattr(assoc.module, 'nome') else None
                    
                modules_used.append(ModuloAssociation(
                    module_id=assoc.module_id,
                    quantidade_padrao=assoc.quantidade_padrao,
                    observacao=assoc.observacao,
                    module_nome=module_nome,
                    created_at=assoc.created_at,
                    updated_at=assoc.updated_at
                ))
        
        # Converter valores de data para string no formato ISO se necessário
        data_validade = None
        if insumo_model.data_validade:
            data_validade = insumo_model.data_validade.isoformat() if hasattr(insumo_model.data_validade, 'isoformat') else str(insumo_model.data_validade)
            
        data_compra = None
        if insumo_model.data_compra:
            data_compra = insumo_model.data_compra.isoformat() if hasattr(insumo_model.data_compra, 'isoformat') else str(insumo_model.data_compra)
        
        # Criar entidade com os valores do modelo
        return InsumoEntity(
            id=insumo_model.id,
            nome=insumo_model.nome,
            descricao=insumo_model.descricao,
            categoria=insumo_model.categoria,
            valor_unitario=float(insumo_model.valor_unitario),
            unidade_medida=insumo_model.unidade_medida,
            estoque_minimo=insumo_model.estoque_minimo,
            estoque_atual=insumo_model.estoque_atual,
            subscriber_id=insumo_model.subscriber_id,
            fornecedor=insumo_model.fornecedor,
            codigo_referencia=insumo_model.codigo_referencia,
            data_validade=data_validade,
            data_compra=data_compra,
            observacoes=insumo_model.observacoes,
            is_active=insumo_model.is_active,
            created_at=insumo_model.created_at,
            updated_at=insumo_model.updated_at,
            modules_used=modules_used
        )
    
    @staticmethod
    def to_model(entity: InsumoEntity, existing_model: Optional[Insumo] = None) -> Insumo:
        """
        Converte uma entidade de domínio em um modelo de banco de dados.
        
        Args:
            entity: Entidade de domínio
            existing_model: Modelo existente a ser atualizado (opcional)
            
        Returns:
            Insumo: Modelo SQLAlchemy correspondente
        """
        if existing_model:
            # Atualizar modelo existente
            insumo_model = existing_model
        else:
            # Criar novo modelo
            insumo_model = Insumo()
            insumo_model.id = entity.id
            insumo_model.created_at = entity.created_at
            
        # Atualizar campos do modelo
        insumo_model.nome = entity.nome
        insumo_model.descricao = entity.descricao
        insumo_model.categoria = entity.categoria
        insumo_model.valor_unitario = entity.valor_unitario
        insumo_model.unidade_medida = entity.unidade_medida
        insumo_model.estoque_minimo = entity.estoque_minimo
        insumo_model.estoque_atual = entity.estoque_atual
        insumo_model.fornecedor = entity.fornecedor
        insumo_model.codigo_referencia = entity.codigo_referencia
        insumo_model.observacoes = entity.observacoes
        insumo_model.is_active = entity.is_active
        insumo_model.updated_at = entity.updated_at
        
        # Tratar data_validade (converter de string para datetime se necessário)
        if entity.data_validade:
            if isinstance(entity.data_validade, str):
                try:
                    insumo_model.data_validade = datetime.fromisoformat(entity.data_validade)
                except ValueError:
                    # Formato de data inválido, registrar erro ou definir como None
                    insumo_model.data_validade = None
            else:
                insumo_model.data_validade = entity.data_validade
        else:
            insumo_model.data_validade = None
        
        # Tratar data_compra (converter de string para datetime se necessário)
        if entity.data_compra:
            if isinstance(entity.data_compra, str):
                try:
                    insumo_model.data_compra = datetime.fromisoformat(entity.data_compra)
                except ValueError:
                    # Formato de data inválido, registrar erro ou definir como None
                    insumo_model.data_compra = None
            else:
                insumo_model.data_compra = entity.data_compra
        else:
            insumo_model.data_compra = None
            
        # Definir subscriber_id (não atualizado em modelos existentes)
        if not existing_model:
            insumo_model.subscriber_id = entity.subscriber_id
            
        return insumo_model
    
    @staticmethod
    def entity_to_dict(entity: InsumoEntity) -> Dict[str, Any]:
        """
        Converte uma entidade de domínio para um dicionário.
        
        Args:
            entity: Entidade de domínio
            
        Returns:
            Dict[str, Any]: Dicionário representando a entidade
        """
        # Converter associações de módulos para dicionários
        modules_used = []
        for module in entity.modules_used:
            modules_used.append({
                "module_id": str(module.module_id),
                "quantidade_padrao": module.quantidade_padrao,
                "observacao": module.observacao,
                "module_nome": module.module_nome,
                "created_at": module.created_at.isoformat() if module.created_at else None,
                "updated_at": module.updated_at.isoformat() if module.updated_at else None
            })
        
        # Criar dicionário com dados da entidade
        return {
            "id": str(entity.id),
            "nome": entity.nome,
            "descricao": entity.descricao,
            "categoria": entity.categoria,
            "valor_unitario": entity.valor_unitario,
            "unidade_medida": entity.unidade_medida,
            "estoque_minimo": entity.estoque_minimo,
            "estoque_atual": entity.estoque_atual,
            "fornecedor": entity.fornecedor,
            "codigo_referencia": entity.codigo_referencia,
            "data_validade": entity.data_validade,
            "data_compra": entity.data_compra,
            "observacoes": entity.observacoes,
            "is_active": entity.is_active,
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
            "subscriber_id": str(entity.subscriber_id),
            "modules_used": modules_used,
            "estoque_baixo": entity.verificar_estoque_baixo(),
            "valor_total": entity.calcular_valor_total()
        }
    
    @staticmethod
    def create_module_associations(
        modules_used: List[ModuloAssociation], 
        insumo_id: UUID
    ) -> List[InsumoModuleAssociation]:
        """
        Cria associações de módulos para um insumo.
        
        Args:
            modules_used: Lista de objetos ModuloAssociation
            insumo_id: ID do insumo
            
        Returns:
            List[InsumoModuleAssociation]: Lista de modelos de associação
        """
        associations = []
        for module in modules_used:
            assoc = InsumoModuleAssociation(
                insumo_id=insumo_id,
                module_id=module.module_id,
                quantidade_padrao=module.quantidade_padrao,
                observacao=module.observacao,
                created_at=module.created_at,
                updated_at=module.updated_at
            )
            associations.append(assoc)
        return associations
    
    @staticmethod
    def update_from_dict(
        model: Insumo, 
        data: Dict[str, Any]
    ) -> Insumo:
        """
        Atualiza um modelo a partir de um dicionário de dados.
        
        Args:
            model: Modelo SQLAlchemy a ser atualizado
            data: Dicionário com os campos a atualizar
            
        Returns:
            Insumo: Modelo atualizado
        """
        # Atualizar campos simples
        fields = [
            "nome", "descricao", "categoria", "valor_unitario", 
            "unidade_medida", "estoque_minimo", "estoque_atual",
            "fornecedor", "codigo_referencia", "observacoes"
        ]
        
        for field in fields:
            if field in data and data[field] is not None:
                setattr(model, field, data[field])
        
        # Atualizar datas (convertendo de string para datetime se necessário)
        if "data_validade" in data and data["data_validade"]:
            if isinstance(data["data_validade"], str):
                try:
                    model.data_validade = datetime.fromisoformat(data["data_validade"])
                except ValueError:
                    # Formato de data inválido, não atualizar
                    pass
            else:
                model.data_validade = data["data_validade"]
        elif "data_validade" in data and data["data_validade"] is None:
            model.data_validade = None
            
        if "data_compra" in data and data["data_compra"]:
            if isinstance(data["data_compra"], str):
                try:
                    model.data_compra = datetime.fromisoformat(data["data_compra"])
                except ValueError:
                    # Formato de data inválido, não atualizar
                    pass
            else:
                model.data_compra = data["data_compra"]
        elif "data_compra" in data and data["data_compra"] is None:
            model.data_compra = None
        
        # Atualizar timestamp
        model.updated_at = datetime.utcnow()
        
        return model